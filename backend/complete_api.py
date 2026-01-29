"""
COMPLETE VIRTUAL TRY-ON API
===========================
All features: Auth, Try-On, History, Wardrobe, Social, Size Recommendations
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict, Field, AliasChoices
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
import uuid
import os
from fastapi.staticfiles import StaticFiles

# -------------------------
# SAFE imports (NO engine)
# -------------------------
from app.models.database import get_db, Base
from app.models import user as user_model
from app.models import tryon_history as history_model
from app.models import wardrobe as wardrobe_model
from app.models import social as social_model

# -------------------------
# Lazy services
# -------------------------
ai_service = None
auth_service = None
size_service = None


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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


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


@app.post("/auth/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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

    with open(rel_path, "wb") as f:
        f.write(contents)

    # Store as a URL path the frontend can load
    current_user.avatar_url = f"/uploads/avatars/{filename}"
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
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result_id = str(uuid.uuid4())

    person_path = f"temp/uploads/{result_id}_person.png"
    cloth_path = f"temp/uploads/{result_id}_cloth.png"
    result_path = f"temp/results/{result_id}_result.png"

    with open(person_path, "wb") as f:
        f.write(await person.read())
    with open(cloth_path, "wb") as f:
        f.write(await cloth.read())

    ai = get_ai_service()
    success = await ai.generate_tryon(
        person_path, cloth_path, result_path, result_id
    )

    if not success:
        raise HTTPException(500, "Try-on failed")

    history = history_model.TryOnHistory(
        user_id=current_user.id,
        result_image_url=result_path
    )

    db.add(history)
    db.commit()

    return {"success": True, "result": result_path}


# =========================
# SIZE RECOMMENDATION (FIXED)
# =========================
@app.post("/api/v1/size/recommend")
async def recommend_size(
    image: UploadFile = File(...),
    user_height_cm: Optional[float] = None,
    current_user: user_model.User = Depends(get_current_user)
):
    service = get_size_service()

    temp_path = f"temp/size_{uuid.uuid4()}.png"
    with open(temp_path, "wb") as f:
        f.write(await image.read())

    try:
        measurements = service.estimate_measurements_from_image(
            temp_path,
            user_height_cm or current_user.height_cm
        )
        return measurements
    finally:
        os.remove(temp_path)
