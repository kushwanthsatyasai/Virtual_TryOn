"""
COMPLETE VIRTUAL TRY-ON API
===========================
All features: Auth, Try-On, History, Wardrobe, Social, Size Recommendations
"""
import os
import logging
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
# Try multiple paths to find .env file
backend_dir = Path(__file__).parent
env_paths = [
    backend_dir / ".env",  # Same directory as complete_api.py
    Path.cwd() / ".env",   # Current working directory
    Path(".env"),          # Relative to current dir
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        env_loaded = True
        print(f"✓ Loaded .env from: {env_path.absolute()}")
        break

if not env_loaded:
    # Fallback: try loading from current directory
    load_dotenv(override=True)

# Cloudinary: optional; when set, try-on results and avatars are uploaded for persistent URLs (Render / mobile)
if os.getenv("CLOUDINARY_URL"):
    print("✓ CLOUDINARY_URL set — media will be stored in Cloudinary")

# AI chat: Gemini only (new SDK: from google import genai)
provider = os.getenv("AI_CHAT_PROVIDER", "gemini")
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"✓ GEMINI_API_KEY loaded: {gemini_key[:20]}...")
else:
    print("⚠ GEMINI_API_KEY not found in .env — chat will be unavailable")
print(f"✓ AI_CHAT_PROVIDER: {provider}")

# Suppress ONNX Runtime GPU discovery warning on headless servers (rembg uses ONNX)
os.environ.setdefault("ORT_LOG_LEVEL", "4")

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict, Field, AliasChoices
from typing import Optional, List, Dict
from datetime import datetime
from contextlib import asynccontextmanager
import uuid
from fastapi.staticfiles import StaticFiles

# Optional: Cloudinary for persistent media URLs (Render / mobile)
def _upload_to_cloudinary(local_path: str, public_id: str, folder: str) -> Optional[str]:
    """Upload a local file to Cloudinary; return secure_url or None if not configured/fails."""
    url = os.getenv("CLOUDINARY_URL")
    if not url or not url.strip():
        return None
    try:
        import cloudinary
        import cloudinary.uploader
        cloudinary.config(cloudinary_url=url)
        r = cloudinary.uploader.upload(
            local_path,
            folder=folder,
            public_id=public_id,
            overwrite=True,
        )
        return r.get("secure_url")
    except Exception as e:
        print(f"⚠ Cloudinary upload failed ({folder}): {e}")
        return None


def _download_temp_file_from_url(url: str) -> Optional[str]:
    """
    Download a remote image to a temp file and return its path.
    Used for avatars stored in Cloudinary when running size recommendation.
    """
    try:
        import requests
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        tmp_path = f"temp/avatar_{uuid.uuid4()}.png"
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(resp.content)
        return tmp_path
    except Exception as e:
        print(f"⚠ Failed to download avatar from URL for sizing: {e}")
        return None

# -------------------------
# SAFE imports (NO engine)
# -------------------------
from app.models.database import get_db, Base
from app.models import user as user_model
from app.models import tryon_history as history_model
from app.models import wardrobe as wardrobe_model
from app.models import social as social_model
from app.models import chat as chat_model

# Module-level logger for detailed request tracing (chat, try-on, sizing, etc.)
logger = logging.getLogger("complete_api")
logger.setLevel(logging.INFO)

# -------------------------
# Lazy services
# -------------------------
ai_service = None
auth_service = None
size_service = None
chat_service = None
recommendation_engine = None


def get_ai_service():
    global ai_service
    if ai_service is None:
        from app.services.ai_service import AIService
        ai_service = AIService()
    return ai_service


def get_auth_service():
    global auth_service
    if auth_service is None:
        from app.services.auth_service import AuthService
        auth_service = AuthService()
    return auth_service


def get_size_service():
    global size_service
    if size_service is None:
        from app.services.size_recommendation_service import SizeRecommendationService
        size_service = SizeRecommendationService()
    return size_service


def get_chat_service():
    global chat_service
    if chat_service is None:
        from app.services.ai_fashion_chat_service import AIFashionChatService
        provider = os.getenv("AI_CHAT_PROVIDER", "gemini")
        chat_service = AIFashionChatService(provider=provider)
    return chat_service


def get_recommendation_engine(db: Session):
    """Get recommendation engine instance (requires DB session)"""
    from app.services.recommendation_service import RecommendationEngine
    return RecommendationEngine(db, use_visual_similarity=True)


# -------------------------
# Lifespan (FAST!)
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ App startup reached")

    # Create folders only (FAST)
    for path in [
        "temp/uploads",
        "temp/results",
        "uploads/avatars",
        "uploads/wardrobe",
        "uploads/posts",
        "static/generated_outputs"
    ]:
        os.makedirs(path, exist_ok=True)

    # Ensure tryon_history.metadata column exists (e.g. existing PostgreSQL DB)
    try:
        from sqlalchemy import text
        from app.models.database import get_engine
        engine = get_engine()
        url = str(engine.url)
        with engine.begin() as conn:
            if "postgresql" in url or "postgres" in url:
                conn.execute(text("ALTER TABLE tryon_history ADD COLUMN IF NOT EXISTS metadata JSONB"))
            else:
                try:
                    conn.execute(text("ALTER TABLE tryon_history ADD COLUMN metadata TEXT"))
                except Exception as col_err:
                    if "duplicate column" not in str(col_err).lower() and "already exists" not in str(col_err).lower():
                        raise
        print("✓ tryon_history.metadata column ensured")
    except Exception as e:
        print(f"⚠ Migration tryon_history.metadata: {e}")

    # ❌ DO NOT run create_all on Render
    yield
    print("🛑 App shutdown")


# -------------------------
# App init
# -------------------------
app = FastAPI(
    title="Virtue Try-On Complete API",
    version="2.0.0",
    lifespan=lifespan
)

# Ensure upload dirs exist before mounting static routes (StaticFiles requires existing dirs)
os.makedirs("uploads/avatars", exist_ok=True)
os.makedirs("temp/results", exist_ok=True)
os.makedirs("temp/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# -------------------------
# Health (REQUIRED)
# -------------------------
@app.get("/")
async def root():
    return {"status": "alive", "service": "Virtue Try-On API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


# =========================
# AUTH HELPERS
# =========================
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    auth = get_auth_service()
    payload = auth.verify_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(user_model.User).filter(
        user_model.User.id == int(payload["sub"])
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =========================
# AUTH ENDPOINTS
# =========================
class UserCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("full_name", "name"))
    age: Optional[int] = None
    phone: Optional[str] = Field(default=None, validation_alias=AliasChoices("phone", "phone_number", "phoneNumber"))
    gender: Optional[str] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    gender: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Full profile for /api/v1/users/me (includes measurements and avatar)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    preferred_size: Optional[str] = None


class UserUpdate(BaseModel):
    """Update profile (all optional, no password)."""
    model_config = ConfigDict(extra="ignore")
    full_name: Optional[str] = Field(default=None, validation_alias=AliasChoices("full_name", "name"))
    age: Optional[int] = None
    phone: Optional[str] = Field(default=None, validation_alias=AliasChoices("phone", "phone_number", "phoneNumber"))
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(default=None, validation_alias=AliasChoices("height_cm", "heightCm"))
    weight_kg: Optional[float] = Field(default=None, validation_alias=AliasChoices("weight_kg", "weightKg"))
    chest_cm: Optional[float] = Field(default=None, validation_alias=AliasChoices("chest_cm", "chestCm"))
    waist_cm: Optional[float] = Field(default=None, validation_alias=AliasChoices("waist_cm", "waistCm"))
    hip_cm: Optional[float] = Field(default=None, validation_alias=AliasChoices("hip_cm", "hipCm"))
    shoulder_width_cm: Optional[float] = None
    preferred_size: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str  # Can be email or username
    password: str


@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth = get_auth_service()

    ok, msg = auth.validate_password_strength(user_data.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)

    username = (user_data.username or str(user_data.email)).strip()
    existing = db.query(user_model.User).filter(
        or_(
            user_model.User.email == str(user_data.email),
            user_model.User.username == username
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = auth.get_password_hash(user_data.password)
    user = user_model.User(
        email=user_data.email,
        username=username,
        hashed_password=hashed,
        full_name=user_data.full_name,
        age=user_data.age,
        phone=user_data.phone,
        gender=user_data.gender,
        chest_cm=user_data.chest_cm,
        waist_cm=user_data.waist_cm,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@app.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-compatible login endpoint.
    
    **Note:** In Swagger UI, you can leave `client_id` and `client_secret` blank - they're optional.
    
    - **username**: Your email or username
    - **password**: Your password
    """
    auth = get_auth_service()
    user = db.query(user_model.User).filter(
        or_(
            user_model.User.username == form.username,
            user_model.User.email == form.username
        )
    ).first()

    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@app.post("/auth/login-simple", response_model=Token, tags=["Auth"])
async def login_simple(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Simple login endpoint (no OAuth2 fields required).
    
    Use this if Swagger's OAuth2 form is confusing.
    Just send JSON: `{"username": "your_email@example.com", "password": "your_password"}`
    """
    auth = get_auth_service()
    user = db.query(user_model.User).filter(
        or_(
            user_model.User.username == credentials.username,
            user_model.User.email == credentials.username
        )
    ).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# =========================
# CURRENT USER PROFILE (GET / PATCH)
# =========================
async def _get_current_user_profile_impl(current_user: user_model.User):
    """Return the authenticated user's full profile (including measurements)."""
    return UserProfileResponse.model_validate(current_user)


@app.get("/api/v1/users/me", response_model=UserProfileResponse, tags=["Profile"])
async def get_current_user_profile(
    current_user: user_model.User = Depends(get_current_user),
):
    return await _get_current_user_profile_impl(current_user)


@app.get("/api/v1/profile/me", response_model=UserProfileResponse, tags=["Profile"])
async def get_current_user_profile_alias(
    current_user: user_model.User = Depends(get_current_user),
):
    """Alias for GET /api/v1/users/me (same response)."""
    return await _get_current_user_profile_impl(current_user)


@app.patch("/api/v1/users/me", response_model=UserProfileResponse, tags=["Profile"])
async def update_current_user_profile(
    payload: UserUpdate,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile. Only provided fields are updated."""
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if hasattr(current_user, key):
            setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return UserProfileResponse.model_validate(current_user)


# =========================
# PROFILE / ONBOARDING
# =========================
@app.post("/api/v1/profile/full-body-photo")
async def upload_full_body_photo(
    photo: UploadFile = File(...),
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not photo.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".heic"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_id = str(uuid.uuid4())
    filename = f"user_{current_user.id}_{file_id}{ext}"
    rel_path = os.path.join("uploads", "avatars", filename)

    contents = await photo.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    # Always save a local copy (for local dev / fallback)
    with open(rel_path, "wb") as f:
        f.write(contents)

    avatar_url: str = f"/uploads/avatars/{filename}"

    # If Cloudinary is configured, upload avatar and prefer its HTTPS URL for persistence
    cloud_url = _upload_to_cloudinary(rel_path, f"avatar_user_{current_user.id}_{file_id}", "virtue-tryon/avatars")
    if cloud_url:
        avatar_url = cloud_url

    # Store avatar URL (either local path or Cloudinary URL)
    current_user.avatar_url = avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"success": True, "avatar_url": current_user.avatar_url}


# =========================
# TRY-ON (FIXED)
# =========================
@app.post("/api/v1/try-on")
async def create_tryon(
    person: UploadFile = File(...),
    cloth: UploadFile = File(...),
    product_id: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    product_image_url: Optional[str] = Form(None),
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start_ts = time.monotonic()
    result_id = str(uuid.uuid4())
    print(f"[TRYON_START] user_id={getattr(current_user, 'id', None)} result_id={result_id} product_id={product_id} product_name={product_name}")
    logger.info(
        "TRYON_START user_id=%s result_id=%s product_id=%s product_name=%s",
        getattr(current_user, "id", None),
        result_id,
        product_id,
        product_name,
    )

    person_path = f"temp/uploads/{result_id}_person.png"
    cloth_path = f"temp/uploads/{result_id}_cloth.png"
    result_path = f"temp/results/{result_id}_result.png"

    with open(person_path, "wb") as f:
        f.write(await person.read())
    with open(cloth_path, "wb") as f:
        f.write(await cloth.read())

    ai = get_ai_service()
    try:
        logger.info(
            "TRYON_CALL service=%s result_id=%s person_path=%s cloth_path=%s",
            getattr(getattr(ai, "service", None), "__class__", type(ai.service)).__name__
            if getattr(ai, "service", None) is not None
            else type(ai).__name__,
            result_id,
            person_path,
            cloth_path,
        )
        print(f"[TRYON_CALL] result_id={result_id} person_path={person_path} cloth_path={cloth_path}")
        success = await ai.generate_tryon(
            person_path, cloth_path, result_path, result_id
        )
    except RuntimeError as e:
        logger.error(
            "TRYON_RUNTIME_ERROR result_id=%s error=%s", result_id, str(e), exc_info=True
        )
        print(f"[TRYON_RUNTIME_ERROR] result_id={result_id} error={e}")
        raise HTTPException(503, str(e))
    except Exception as e:
        logger.error(
            "TRYON_EXCEPTION result_id=%s error=%s", result_id, str(e), exc_info=True
        )
        print(f"[TRYON_EXCEPTION] result_id={result_id} error={e}")
        raise HTTPException(
            503, "Try-on service temporarily unavailable. Please try again later."
        )

    if not success:
        logger.error("TRYON_FAILED result_id=%s success_flag_false", result_id)
        print(f"[TRYON_FAILED] result_id={result_id} success_flag_false")
        raise HTTPException(
            503, "Try-on service temporarily unavailable. Please try again later."
        )

    metadata = None
    if product_id or product_name or product_image_url:
        metadata = {
            k: v for k, v in [
                ("product_id", product_id),
                ("product_name", product_name),
                ("product_image_url", product_image_url),
            ] if v
        }

    # Ensure result file exists (saved by ai.generate_tryon to result_path)
    if not os.path.isfile(result_path):
        logger.error("TRYON_MISSING_RESULT_FILE result_id=%s path=%s", result_id, result_path)
        print(f"[TRYON_MISSING_RESULT_FILE] result_id={result_id} path={result_path}")
        raise HTTPException(503, "Try-on output was not saved. Please try again.")

    # Optional: upload to Cloudinary so images persist on Render and are visible on mobile
    result_image_stored = result_path
    public_id = f"result_{result_id}"
    cloudinary_url = _upload_to_cloudinary(result_path, public_id, "virtue-tryon/results")
    if cloudinary_url:
        result_image_stored = cloudinary_url

    history = history_model.TryOnHistory(
        user_id=current_user.id,
        person_image_url=person_path,
        cloth_image_url=cloth_path,
        result_image_url=result_image_stored,
        metadata_=metadata,
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    # result_url: full URL (Cloudinary) or path (local) for display
    if result_image_stored.startswith("http"):
        result_url = result_image_stored
    else:
        result_url = (
            f"/{result_image_stored}"
            if not result_image_stored.startswith("/")
            else result_image_stored
        )

    elapsed = time.monotonic() - start_ts
    logger.info(
        "TRYON_SUCCESS user_id=%s result_id=%s history_id=%s duration_sec=%.2f result_url=%s",
        getattr(current_user, "id", None),
        result_id,
        history.id,
        elapsed,
        result_url,
    )
    print(f"[TRYON_SUCCESS] user_id={getattr(current_user, 'id', None)} result_id={result_id} history_id={history.id} duration_sec={elapsed:.2f} result_url={result_url}")

    return {
        "success": True,
        "result": result_path,
        "result_url": result_url,
        "history_id": history.id,
        "output_saved": True,
    }


# =========================
# TRY-ON HISTORY (for Recent Looks)
# =========================
@app.get("/api/v1/try-on/history")
async def get_tryon_history(
    skip: int = 0,
    limit: int = 20,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List current user's try-on history (for Recent Looks on home)."""
    rows = (
        db.query(history_model.TryOnHistory)
        .filter(history_model.TryOnHistory.user_id == current_user.id)
        .order_by(history_model.TryOnHistory.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    out = []
    for r in rows:
        # Return paths relative to API base so frontend can use its configured base URL
        result_path = r.result_image_url if (r.result_image_url or "").startswith("http") else f"/{r.result_image_url}"
        cloth_path = (r.cloth_image_url if (r.cloth_image_url or "").startswith("http") else f"/{r.cloth_image_url}") if r.cloth_image_url else None
        out.append({
            "id": r.id,
            "result_image_url": result_path,
            "cloth_image_url": cloth_path,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "metadata": r.metadata_ or {},
        })
    return {"items": out}


# =========================
# SIZE RECOMMENDATION (FIXED)
# =========================
@app.post("/api/v1/size/recommend")
async def recommend_size(
    image: UploadFile = File(...),
    user_height_cm: Optional[float] = None,
    garment_type: Optional[str] = Query("shirt"),
    current_user: user_model.User = Depends(get_current_user)
):
    service = get_size_service()

    temp_path = f"temp/size_{uuid.uuid4()}.png"
    with open(temp_path, "wb") as f:
        f.write(await image.read())

    try:
        measurements = service.estimate_measurements_from_image(
            temp_path,
            user_height_cm or getattr(current_user, "height_cm", None)
        )
        rec = service.recommend_size(measurements, garment_type=garment_type or "shirt", gender="unisex")
        return {
            "measurements": measurements,
            "recommended_size": rec["recommended_size"],
            "confidence": rec["confidence"],
            "fit_notes": rec.get("fit_notes", ""),
        }
    finally:
        if os.path.isfile(temp_path):
            os.remove(temp_path)


@app.get("/api/v1/size/recommend")
async def recommend_size_from_profile(
    garment_type: Optional[str] = Query("shirt"),
    current_user: user_model.User = Depends(get_current_user),
):
    """Get AI size recommendation using the current user's profile (full-body) photo, local or Cloudinary."""
    avatar_url = getattr(current_user, "avatar_url", None) or ""
    if not avatar_url or not avatar_url.strip():
        raise HTTPException(400, "Upload a full-body photo in Profile to get AI size recommendation.")

    # Resolve avatar source: prefer Cloudinary/remote URL first, then fall back to local avatar file
    temp_avatar_path: Optional[str] = None
    try:
        path: Optional[str] = None

        # 1) Try Cloudinary/remote URL from avatar_url (if it is an http/https URL)
        if avatar_url.startswith("http://") or avatar_url.startswith("https://"):
            temp_avatar_path = _download_temp_file_from_url(avatar_url)
            if temp_avatar_path and os.path.isfile(temp_avatar_path):
                path = temp_avatar_path

        # 2) If remote download failed or avatar_url is not http/https, try to find a local avatar file
        if path is None:
            try:
                import glob

                # Prefer latest local avatar for this user (matches upload filename pattern)
                pattern = os.path.join("uploads", "avatars", f"user_{current_user.id}_*")
                local_candidates = glob.glob(pattern)
                if local_candidates:
                    local_candidates.sort(key=os.path.getmtime, reverse=True)
                    candidate = local_candidates[0]
                    if os.path.isfile(candidate):
                        path = candidate
            except Exception:
                path = None

        # 3) If still no path, resolve from avatar_url as relative local path
        if path is None:
            # Local relative path, e.g. /uploads/avatars/xxx.png
            path = avatar_url.lstrip("/").replace("\\", "/")
            if not path.startswith("uploads/"):
                path = (
                    f"uploads/avatars/{path.split('/')[-1]}"
                    if "/" in path
                    else f"uploads/avatars/{path}"
                )
            if not os.path.isfile(path):
                raise HTTPException(
                    400,
                    "Profile photo not found or not accessible. Please upload a full-body photo in Profile again.",
                )

        service = get_size_service()
        measurements = service.estimate_measurements_from_image(
            path,
            getattr(current_user, "height_cm", None),
        )
        rec = service.recommend_size(measurements, garment_type=garment_type or "shirt", gender="unisex")
        return {
            "recommended_size": rec["recommended_size"],
            "confidence": rec["confidence"],
            "fit_notes": rec.get("fit_notes", ""),
        }
    finally:
        # Clean up temp file if we downloaded from URL
        if temp_avatar_path and os.path.isfile(temp_avatar_path):
            try:
                os.remove(temp_avatar_path)
            except Exception:
                pass


# =========================
# AI FASHION CHAT
# =========================
class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    message: str
    conversation_id: int
    model: Optional[str] = None
    usage: Optional[Dict] = None


@app.post("/api/v1/chat/send", response_model=ChatMessageResponse, tags=["AI Chat"])
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI fashion assistant.
    
    The AI will provide personalized fashion advice based on:
    - Your style preferences
    - Try-on history
    - Wardrobe items
    - Current fashion trends
    
    **Note:** Requires API key configuration:
    - Set `OPENAI_API_KEY` in environment variables for OpenAI
    - Or set `ANTHROPIC_API_KEY` for Anthropic Claude
    - Or use `ollama` provider for local models (no API key needed)
    """
    chat = get_chat_service()
    
    # Get or create conversation
    if request.conversation_id:
        conversation = db.query(chat_model.Conversation).filter(
            chat_model.Conversation.id == request.conversation_id,
            chat_model.Conversation.user_id == current_user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = chat_model.Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Get conversation history
    history_messages = db.query(chat_model.ChatMessage).filter(
        chat_model.ChatMessage.conversation_id == conversation.id
    ).order_by(chat_model.ChatMessage.created_at).all()
    
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]
    
    # Build user context
    user_context = {
        "user_id": current_user.id,
        "age": current_user.age,
        "gender": current_user.gender,
        "style_tags": current_user.style_tags or [],
        "favorite_colors": current_user.favorite_colors or [],
        "favorite_brands": current_user.favorite_brands or [],
    }
    
    # Get AI response
    start_ts = time.monotonic()
    try:
        # Check if chat service is available
        if chat.client is None and chat.provider != "ollama":
            api_key_name = (
                "GEMINI_API_KEY" if chat.provider == "gemini" else f"{chat.provider.upper()}_API_KEY"
            )
            logger.error(
                "CHAT_CONFIG_ERROR user_id=%s provider=%s missing_key=%s",
                current_user.id,
                chat.provider,
                api_key_name,
            )
            raise HTTPException(
                status_code=503,
                detail=f"AI chat service not configured. Please set {api_key_name} in .env file and restart the server.",
            )

        logger.info(
            "CHAT_START user_id=%s provider=%s model=%s conversation_id=%s",
            current_user.id,
            chat.provider,
            getattr(chat, "model", None),
            conversation.id,
        )

        result = chat.chat(
            user_message=request.message,
            user_context=user_context,
            conversation_history=conversation_history,
        )

        # Check if result contains an error (e.g. quota exceeded, provider issues)
        if "error" in result:
            # For Gemini, surface quota / 429 errors clearly
            error_text = str(result.get("error", "")).lower()
            response_text = result.get("response", "") or "AI chat service unavailable"

            logger.error(
                "CHAT_PROVIDER_ERROR user_id=%s provider=%s model=%s error=%s",
                current_user.id,
                chat.provider,
                getattr(chat, "model", None),
                result.get("error"),
            )

            if chat.provider == "gemini" and ("quota" in error_text or "429" in error_text):
                raise HTTPException(
                    status_code=503,
                    detail="Gemini chat quota has been exceeded for this project. "
                    "Please upgrade your Gemini plan or switch AI_CHAT_PROVIDER to a different provider (e.g. openai, anthropic, ollama).",
                )

            raise HTTPException(
                status_code=503,
                detail=response_text,
            )

        ai_response = result.get("response", "I'm sorry, I couldn't generate a response.")

        # Save user message
        user_msg = chat_model.ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)

        # Save AI response
        ai_msg = chat_model.ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            message_metadata={
                "model": result.get("model"),
                "usage": result.get("usage", {}),
            },
        )
        db.add(ai_msg)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db.commit()

        elapsed = time.monotonic() - start_ts
        logger.info(
            "CHAT_SUCCESS user_id=%s provider=%s model=%s conversation_id=%s duration_sec=%.2f",
            current_user.id,
            chat.provider,
            result.get("model"),
            conversation.id,
            elapsed,
        )

        return ChatMessageResponse(
            message=ai_response,
            conversation_id=conversation.id,
            model=result.get("model"),
            usage=result.get("usage"),
        )

    except HTTPException:
        # Preserve HTTPExceptions we raised above
        db.rollback()
        logger.exception(
            "CHAT_HTTP_EXCEPTION user_id=%s provider=%s conversation_id=%s",
            current_user.id,
            getattr(chat, "provider", None),
            conversation.id if 'conversation' in locals() else None,
        )
        raise
    except Exception as e:
        db.rollback()
        # Provider-aware guidance for configuration issues
        provider = getattr(chat, "provider", None) or os.getenv("AI_CHAT_PROVIDER", "gemini")
        provider_env = "GEMINI_API_KEY" if provider == "gemini" else f"{provider.upper()}_API_KEY"
        logger.exception(
            "CHAT_UNEXPECTED_ERROR user_id=%s provider=%s model=%s conversation_id=%s error=%s",
            current_user.id,
            provider,
            getattr(chat, "model", None),
            conversation.id if 'conversation' in locals() else None,
            str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=(
                f"Chat service error: {str(e)}. "
                f"Make sure {provider_env} is set in .env or switch AI_CHAT_PROVIDER to a configured provider."
            ),
        )


# =========================
# RECOMMENDATIONS
# =========================
@app.get("/api/v1/recommendations", tags=["Recommendations"])
async def get_recommendations(
    limit: int = 20,
    category: Optional[str] = None,
    exclude_tried: bool = False,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized clothing recommendations.
    
    Uses multiple strategies:
    - Try-on history analysis
    - Favorite items similarity
    - Wardrobe-based recommendations
    - Similar users (collaborative filtering)
    - Trending items
    - Visual similarity (ResNet-based)
    """
    engine = get_recommendation_engine(db)
    
    try:
        recommendations = engine.get_recommendations(
            user_id=current_user.id,
            limit=limit,
            category=category,
            exclude_tried=exclude_tried
        )
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation engine error: {str(e)}"
        )
