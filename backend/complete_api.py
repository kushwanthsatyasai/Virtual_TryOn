"""
COMPLETE VIRTUAL TRY-ON API
===========================
All features: Auth, Try-On, History, Wardrobe, Social, Size Recommendations
"""
import os
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

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
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

# -------------------------
# SAFE imports (NO engine)
# -------------------------
from app.models.database import get_db, Base
from app.models import user as user_model
from app.models import tryon_history as history_model
from app.models import wardrobe as wardrobe_model
from app.models import social as social_model
from app.models import chat as chat_model

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
    try:
        # Check if chat service is available
        if chat.client is None and chat.provider != "ollama":
            api_key_name = "GEMINI_API_KEY" if chat.provider == "gemini" else f"{chat.provider.upper()}_API_KEY"
            raise HTTPException(
                status_code=503,
                detail=f"AI chat service not configured. Please set {api_key_name} in .env file and restart the server."
            )
        
        result = chat.chat(
            user_message=request.message,
            user_context=user_context,
            conversation_history=conversation_history
        )
        
        # Check if result contains an error
        if "error" in result:
            raise HTTPException(
                status_code=503,
                detail=result.get("response", "AI chat service unavailable")
            )
        
        ai_response = result.get("response", "I'm sorry, I couldn't generate a response.")
        
        # Save user message
        user_msg = chat_model.ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_msg)
        
        # Save AI response
        ai_msg = chat_model.ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            message_metadata={
                "model": result.get("model"),
                "usage": result.get("usage", {})
            }
        )
        db.add(ai_msg)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return ChatMessageResponse(
            message=ai_response,
            conversation_id=conversation.id,
            model=result.get("model"),
            usage=result.get("usage")
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}. Make sure OPENAI_API_KEY or ANTHROPIC_API_KEY is set in .env"
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
