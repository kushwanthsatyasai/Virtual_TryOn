"""
COMPLETE VIRTUAL TRY-ON API
===========================
All features: Auth, Try-On, History, Wardrobe, Social, Size Recommendations
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
import uuid
import os

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
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    auth = get_auth_service()

    hashed = auth.get_password_hash(user_data.password)
    user = user_model.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@app.post("/auth/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth = get_auth_service()
    user = db.query(user_model.User).filter(
        user_model.User.username == form.username
    ).first()

    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


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
