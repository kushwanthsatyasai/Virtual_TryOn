"""
COMPLETE VIRTUAL TRY-ON API
===========================
All features: Auth, Try-On, History, Wardrobe, Social, Size Recommendations
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uuid
import os
import shutil
import sys

# Import models and services
from app.models.database import get_db, engine, Base
from app.models import user as user_model
from app.models import tryon_history as history_model
from app.models import wardrobe as wardrobe_model
from app.models import social as social_model
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.size_recommendation_service import SizeRecommendationService
from app.core.config import settings

# Create tables (with error handling for deployment)
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created/verified")
except Exception as e:
    print(f"⚠ Warning: Database initialization error: {e}")
    print("App will continue but database features may not work.")

# Initialize services (global) - with error handling
ai_service = None

def get_ai_service():
    """Lazy load AI service - only initialize when needed"""
    global ai_service
    if ai_service is None:
        try:
            print("Initializing AI Service (lazy load)...")
            sys.stdout.flush()
            ai_service = AIService()
            print("✓ AI Service initialized")
            sys.stdout.flush()
        except Exception as e:
            print(f"⚠ Warning: AI Service initialization failed: {e}")
            sys.stdout.flush()
            raise HTTPException(
                status_code=503,
                detail="AI Service is not available. Please try again later."
            )
    return ai_service

try:
    auth_service = AuthService()
    size_service = SizeRecommendationService()
except Exception as e:
    print(f"⚠ Warning: Service initialization error: {e}")
    auth_service = None
    size_service = None

# Lifespan event handler - MUST be fast and non-blocking
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - FAST and non-blocking (critical for Render port detection)
    global ai_service
    
    # Create directories (fast operation, non-blocking)
    try:
        os.makedirs("temp/uploads", exist_ok=True)
        os.makedirs("temp/results", exist_ok=True)
        os.makedirs("uploads/avatars", exist_ok=True)
        os.makedirs("uploads/wardrobe", exist_ok=True)
        os.makedirs("static/generated_outputs", exist_ok=True)
    except:
        pass  # Ignore errors, continue
    
    # Don't initialize AI service here - it's too slow and blocks startup
    # Initialize it lazily when first needed via get_ai_service()
    ai_service = None
    
    # Server is ready immediately - this allows port binding
    # Render will detect the port once this yields
    yield
    # Shutdown (cleanup if needed)

# Initialize app with lifespan
app = FastAPI(
    title="Virtue Try-On Complete API",
    version="2.0.0",
    description="Full-featured virtual try-on with social features",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ============================================
# PYDANTIC MODELS
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_premium: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TryOnCreate(BaseModel):
    quality: str = "balanced"
    cloth_type: Optional[str] = None
    tags: Optional[List[str]] = None

class WardrobeItemCreate(BaseModel):
    name: str
    category: str
    color: Optional[str] = None
    brand: Optional[str] = None
    season: Optional[List[str]] = None

class OutfitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    item_ids: List[int]

class PostCreate(BaseModel):
    caption: Optional[str] = None
    tryon_id: Optional[int] = None
    tags: Optional[str] = None


# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    payload = auth_service.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(user_model.User).filter(
        (user_model.User.email == user_data.email) |
        (user_model.User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Validate password
    is_valid, message = auth_service.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Create user
    hashed_password = auth_service.get_password_hash(user_data.password)
    new_user = user_model.User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = auth_service.create_access_token(data={"sub": str(new_user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user"""
    user = db.query(user_model.User).filter(
        user_model.User.username == form_data.username
    ).first()
    
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: user_model.User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)


# ============================================
# VIRTUAL TRY-ON ENDPOINTS
# ============================================

@app.post("/api/v1/try-on")
async def create_tryon(
    person: UploadFile = File(...),
    cloth: UploadFile = File(...),
    quality: str = "balanced",
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate virtual try-on (authenticated)"""
    result_id = str(uuid.uuid4())
    
    # Save files
    person_path = f"temp/uploads/{result_id}_person.png"
    cloth_path = f"temp/uploads/{result_id}_cloth.png"
    result_path = f"temp/results/{result_id}_result.png"
    
    with open(person_path, "wb") as f:
        f.write(await person.read())
    
    with open(cloth_path, "wb") as f:
        f.write(await cloth.read())
    
    # Generate try-on
    start_time = datetime.now()
    
    # Lazy load AI service
    ai = get_ai_service()
    success = await ai.generate_tryon(
        user_image_path=person_path,
        cloth_image_path=cloth_path,
        output_path=result_path,
        session_id=result_id
    )
    
    processing_time = (datetime.now() - start_time).total_seconds()
    
    if success:
        # Save to history
        tryon = history_model.TryOnHistory(
            user_id=current_user.id,
            person_image_url=f"/uploads/{result_id}_person.png",
            cloth_image_url=f"/uploads/{result_id}_cloth.png",
            result_image_url=f"/uploads/{result_id}_result.png",
            quality_preset=quality,
            processing_time=processing_time
        )
        
        db.add(tryon)
        db.commit()
        db.refresh(tryon)
        
        return {
            "success": True,
            "tryon_id": tryon.id,
            "result_url": f"/api/v1/results/{result_id}",
            "processing_time": processing_time
        }
    
    raise HTTPException(status_code=500, detail="Try-on generation failed")


@app.get("/api/v1/history")
async def get_history(
    skip: int = 0,
    limit: int = 20,
    favorites_only: bool = False,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get try-on history"""
    query = db.query(history_model.TryOnHistory).filter(
        history_model.TryOnHistory.user_id == current_user.id
    )
    
    if favorites_only:
        query = query.filter(history_model.TryOnHistory.is_favorite == True)
    
    tryons = query.order_by(history_model.TryOnHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": len(tryons), "items": tryons}


@app.post("/api/v1/history/{tryon_id}/favorite")
async def toggle_favorite(
    tryon_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle favorite status"""
    tryon = db.query(history_model.TryOnHistory).filter(
        history_model.TryOnHistory.id == tryon_id,
        history_model.TryOnHistory.user_id == current_user.id
    ).first()
    
    if not tryon:
        raise HTTPException(status_code=404, detail="Try-on not found")
    
    tryon.is_favorite = not tryon.is_favorite
    db.commit()
    
    return {"is_favorite": tryon.is_favorite}


# ============================================
# WARDROBE ENDPOINTS
# ============================================

@app.post("/api/v1/wardrobe")
async def add_wardrobe_item(
    name: str,
    category: str,
    image: UploadFile = File(...),
    color: Optional[str] = None,
    brand: Optional[str] = None,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to wardrobe"""
    item_id = str(uuid.uuid4())
    image_path = f"uploads/wardrobe/{item_id}.png"
    
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    item = wardrobe_model.WardrobeItem(
        user_id=current_user.id,
        name=name,
        category=category,
        image_url=image_path,
        color=color,
        brand=brand
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {"id": item.id, "name": item.name}


@app.get("/api/v1/wardrobe")
async def get_wardrobe(
    category: Optional[str] = None,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wardrobe items"""
    query = db.query(wardrobe_model.WardrobeItem).filter(
        wardrobe_model.WardrobeItem.user_id == current_user.id,
        wardrobe_model.WardrobeItem.is_active == True
    )
    
    if category:
        query = query.filter(wardrobe_model.WardrobeItem.category == category)
    
    items = query.all()
    return {"total": len(items), "items": items}


# ============================================
# RECOMMENDATION ENGINE ENDPOINTS
# ============================================

@app.get("/api/v1/recommendations")
async def get_recommendations(
    limit: int = 20,
    category: Optional[str] = None,
    exclude_tried: bool = False,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized clothing recommendations
    
    Based on:
    - User's try-on history
    - Favorites
    - Wardrobe
    - Similar users
    - Trending items
    """
    from app.services.recommendation_service import get_recommendation_service
    
    rec_service = get_recommendation_service(db)
    recommendations = rec_service.get_recommendations(
        user_id=current_user.id,
        limit=limit,
        category=category,
        exclude_tried=exclude_tried
    )
    
    return {
        "total": len(recommendations),
        "recommendations": recommendations,
        "user_id": current_user.id
    }


@app.get("/api/v1/recommendations/style-profile")
async def get_style_profile(
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's style profile and preferences"""
    from app.services.recommendation_service import get_recommendation_service
    
    rec_service = get_recommendation_service(db)
    profile = rec_service.get_user_style_profile(current_user.id)
    
    return profile


@app.post("/api/v1/recommendations/interaction")
async def record_interaction(
    item_id: str,
    interaction_type: str,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record user interaction with recommended item
    
    Interaction types:
    - view: User viewed the item
    - click: User clicked on the item
    - try: User tried on the item
    - favorite: User favorited the item
    - purchase: User purchased the item
    - ignore: User dismissed the recommendation
    """
    from app.services.recommendation_service import get_recommendation_service
    from app.models.recommendations import RecommendationInteraction
    
    # Record interaction
    interaction = RecommendationInteraction(
        user_id=current_user.id,
        item_id=item_id,
        interaction_type=interaction_type
    )
    db.add(interaction)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Recorded {interaction_type} interaction for item {item_id}"
    }


@app.get("/api/v1/recommendations/similar/{item_id}")
async def get_similar_items(
    item_id: str,
    limit: int = 10,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items similar to a specific item"""
    # Mock implementation - in production, use actual similarity search
    return {
        "item_id": item_id,
        "similar_items": [
            {
                "id": f"similar_{i}",
                "name": f"Similar Item {i}",
                "similarity_score": 0.9 - (i * 0.05),
                "reason": "Similar style and color"
            }
            for i in range(1, limit + 1)
        ]
    }


@app.get("/api/v1/recommendations/trending")
async def get_trending_items(
    category: Optional[str] = None,
    days: int = 7,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trending items based on recent try-ons"""
    from app.services.recommendation_service import get_recommendation_service
    
    rec_service = get_recommendation_service(db)
    trending = rec_service._trending_items(category)
    
    # Convert to list and limit
    trending_list = [
        {
            "item_id": item_id,
            "popularity_score": score,
            "category": category or "all"
        }
        for item_id, score in sorted(trending.items(), key=lambda x: x[1], reverse=True)[:limit]
    ]
    
    return {
        "total": len(trending_list),
        "trending_items": trending_list,
        "period_days": days
    }


# ============================================
# VISUAL SIMILARITY ENDPOINTS (Fashion Recommendation)
# ============================================

@app.post("/api/v1/visual/similar-by-image")
async def get_similar_by_image(
    image: UploadFile = File(...),
    limit: int = 10,
    category: Optional[str] = None,
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Find visually similar clothing items using deep learning.
    
    Upload an image and get recommendations for visually similar items.
    Uses ResNet-based feature extraction and nearest neighbor search.
    """
    from app.services.visual_similarity_service import get_visual_recommendation_service
    
    # Save uploaded image temporarily
    temp_path = f"temp/visual_query_{uuid.uuid4()}.png"
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    
    try:
        # Get visual similarity service
        visual_service = get_visual_recommendation_service()
        
        # Find similar items
        similar_items = visual_service.get_similar_items_by_image(
            image_path=temp_path,
            k=limit,
            category_filter=category
        )
        
        return {
            "total": len(similar_items),
            "similar_items": similar_items,
            "method": "visual_similarity",
            "model": "ResNet50"
        }
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/api/v1/visual/similar-by-id/{item_id}")
async def get_similar_by_id(
    item_id: str,
    limit: int = 10,
    category: Optional[str] = None,
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Find visually similar items to a specific item.
    
    Returns items that look similar based on visual features.
    """
    from app.services.visual_similarity_service import get_visual_recommendation_service
    
    visual_service = get_visual_recommendation_service()
    
    similar_items = visual_service.get_similar_items_by_id(
        item_id=item_id,
        k=limit,
        category_filter=category
    )
    
    return {
        "item_id": item_id,
        "total": len(similar_items),
        "similar_items": similar_items,
        "method": "visual_similarity"
    }


@app.post("/api/v1/visual/add-item")
async def add_item_to_visual_index(
    item_id: str,
    image: UploadFile = File(...),
    name: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    price: Optional[float] = None,
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Add a new item to the visual similarity index.
    
    This allows the system to recommend this item when users search for similar items.
    """
    from app.services.visual_similarity_service import get_visual_recommendation_service
    
    # Save image
    image_path = f"uploads/visual_catalog/{item_id}.png"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    # Prepare metadata
    metadata = {
        'name': name,
        'category': category,
        'brand': brand,
        'price': price,
        'image_url': f"/static/catalog/{item_id}.png"
    }
    
    # Add to visual index
    visual_service = get_visual_recommendation_service()
    visual_service.add_item_to_index(
        item_id=item_id,
        image_path=image_path,
        metadata=metadata
    )
    
    return {
        "status": "success",
        "message": f"Item {item_id} added to visual similarity index",
        "item_id": item_id
    }


@app.get("/api/v1/visual/recommendations")
async def get_visual_recommendations(
    limit: int = 20,
    category: Optional[str] = None,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get visual recommendations based on user's try-on history.
    
    Analyzes what the user has tried on and recommends visually similar items.
    Combines collaborative filtering with visual similarity.
    """
    from app.services.visual_similarity_service import get_visual_recommendation_service
    from app.models.tryon_history import TryOnHistory
    
    # Get user's recent try-ons
    recent_tryons = (
        db.query(TryOnHistory)
        .filter(TryOnHistory.user_id == current_user.id)
        .order_by(TryOnHistory.created_at.desc())
        .limit(10)
        .all()
    )
    
    if not recent_tryons:
        return {
            "total": 0,
            "recommendations": [],
            "message": "No try-on history found. Try on some items first!"
        }
    
    # Get visual service
    visual_service = get_visual_recommendation_service()
    
    # Collect recommendations from recent try-ons
    all_recommendations = []
    seen_items = set()
    
    for tryon in recent_tryons:
        # Use the cloth image from try-on
        if hasattr(tryon, 'cloth_image_path') and tryon.cloth_image_path:
            similar = visual_service.get_similar_items_by_image(
                image_path=tryon.cloth_image_path,
                k=5,
                category_filter=category
            )
            
            for item in similar:
                if item['item_id'] not in seen_items:
                    item['reason'] = f"Similar to item you tried on {tryon.created_at.strftime('%Y-%m-%d')}"
                    all_recommendations.append(item)
                    seen_items.add(item['item_id'])
    
    # Sort by similarity score and limit
    all_recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    all_recommendations = all_recommendations[:limit]
    
    return {
        "total": len(all_recommendations),
        "recommendations": all_recommendations,
        "based_on_tryons": len(recent_tryons),
        "method": "visual_similarity_from_history"
    }


# ============================================
# FASHION METADATA & SMART SEARCH (No RAG Needed!)
# ============================================

@app.post("/api/v1/fashion/enhance-product")
async def enhance_product_metadata(
    item_id: str,
    name: str,
    category: str,
    description: Optional[str] = None,
    material: Optional[str] = None,
    image: Optional[UploadFile] = File(None),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Enhance product with rich fashion metadata (no RAG database needed!).
    
    Automatically adds:
    - Style tags (casual, formal, bohemian, etc.)
    - Suitable occasions (work, party, casual, etc.)
    - Seasonal recommendations
    - Care instructions
    - Styling tips
    - Color analysis (if image provided)
    """
    from app.services.fashion_metadata_service import get_fashion_metadata_enhancer
    
    # Prepare product data
    product = {
        'id': item_id,
        'name': name,
        'category': category,
        'description': description or '',
        'material': material or ''
    }
    
    # Save image if provided
    if image:
        image_path = f"uploads/products/{item_id}.png"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(await image.read())
        product['image_path'] = image_path
    
    # Enhance with metadata
    enhancer = get_fashion_metadata_enhancer()
    enhanced_product = enhancer.enhance_product(
        product,
        extract_from_image=bool(image)
    )
    
    return {
        "status": "success",
        "product": enhanced_product,
        "message": "Product enhanced with fashion metadata"
    }


@app.get("/api/v1/fashion/search")
async def smart_fashion_search(
    style: Optional[str] = None,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    color: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Smart fashion search without RAG database.
    
    Search by:
    - Style: casual, formal, bohemian, sporty, etc.
    - Occasion: work, party, wedding, beach, etc.
    - Season: spring, summer, fall, winter
    - Color: red, blue, black, white, etc.
    - Category: top, bottom, dress, etc.
    
    Example: Find casual summer dresses in blue
    """
    from app.services.fashion_metadata_service import get_fashion_metadata_enhancer
    
    # In production, get from your product catalog
    # For now, demonstrate with user's wardrobe
    from app.models.wardrobe import WardrobeItem
    
    wardrobe_items = (
        db.query(WardrobeItem)
        .filter(WardrobeItem.user_id == current_user.id)
        .all()
    )
    
    # Convert to product format
    products = []
    for item in wardrobe_items:
        product = {
            'id': str(item.id),
            'name': item.name,
            'category': item.category,
            'style_tags': item.tags or [],
            'occasions': [],
            'seasons': item.season.split(',') if item.season else [],
            'color_palette': []
        }
        products.append(product)
    
    # Filter by criteria
    enhancer = get_fashion_metadata_enhancer()
    filtered = enhancer.search_by_criteria(
        products=products,
        style=style,
        occasion=occasion,
        season=season,
        color=color
    )
    
    # Apply category filter
    if category:
        filtered = [p for p in filtered if category in p.get('category', '').lower()]
    
    return {
        "total": len(filtered),
        "results": filtered[:limit],
        "filters_applied": {
            "style": style,
            "occasion": occasion,
            "season": season,
            "color": color,
            "category": category
        }
    }


@app.post("/api/v1/fashion/outfit-suggestions")
async def get_outfit_suggestions(
    item_id: str,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get outfit suggestions for an item (no RAG needed!).
    
    Suggests complementary items based on:
    - Style compatibility
    - Occasion matching
    - Category pairing (e.g., top + bottom)
    """
    from app.services.fashion_metadata_service import get_fashion_metadata_enhancer
    from app.models.wardrobe import WardrobeItem
    
    # Get the target item
    target_item = (
        db.query(WardrobeItem)
        .filter(
            WardrobeItem.user_id == current_user.id,
            WardrobeItem.id == int(item_id)
        )
        .first()
    )
    
    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get all other items
    other_items = (
        db.query(WardrobeItem)
        .filter(
            WardrobeItem.user_id == current_user.id,
            WardrobeItem.id != int(item_id)
        )
        .all()
    )
    
    # Convert to product format
    target = {
        'id': str(target_item.id),
        'name': target_item.name,
        'category': target_item.category,
        'style_tags': target_item.tags or [],
        'occasions': []
    }
    
    available = [
        {
            'id': str(item.id),
            'name': item.name,
            'category': item.category,
            'style_tags': item.tags or [],
            'occasions': [],
            'image_url': item.image_url
        }
        for item in other_items
    ]
    
    # Get suggestions
    enhancer = get_fashion_metadata_enhancer()
    suggestions = enhancer.get_outfit_suggestions(target, available)
    
    return {
        "item": target,
        "suggestions": suggestions,
        "total": len(suggestions),
        "message": f"Found {len(suggestions)} items that go well with this"
    }


# ============================================
# AI FASHION CHAT ASSISTANT 🤖
# ============================================

@app.post("/api/v1/chat/send")
async def send_chat_message(
    message: str,
    conversation_id: Optional[int] = None,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI fashion assistant.
    
    The AI will provide personalized fashion advice based on:
    - Your style profile and preferences
    - Your try-on history
    - Your wardrobe
    - Current fashion trends
    
    Example queries:
    - "What should I wear to a summer wedding?"
    - "Recommend casual outfits for weekend"
    - "What goes well with a blue striped shirt?"
    - "I need formal attire for an interview"
    """
    from app.services.ai_fashion_chat_service import (
        get_ai_fashion_chat_service,
        ConversationManager
    )
    
    conv_manager = ConversationManager(db)
    
    # Create or get conversation
    if conversation_id is None:
        conversation_id = conv_manager.create_conversation(
            user_id=current_user.id,
            title=message[:50] + "..." if len(message) > 50 else message
        )
    
    # Get conversation history
    history = conv_manager.get_conversation_history(conversation_id)
    
    # Save user message
    conv_manager.add_message(
        conversation_id=conversation_id,
        role="user",
        content=message
    )
    
    # Get user context
    chat_service = get_ai_fashion_chat_service()
    
    # Build user context
    from app.services.recommendation_service import get_recommendation_service
    rec_service = get_recommendation_service(db)
    
    try:
        user_context = {
            'style_profile': rec_service.get_user_style_profile(current_user.id),
            'user_id': current_user.id
        }
    except:
        user_context = {'user_id': current_user.id}
    
    # Get AI response
    ai_response = chat_service.chat(
        user_message=message,
        user_context=user_context,
        conversation_history=history
    )
    
    # Save assistant message
    conv_manager.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response.get('response', 'Sorry, I could not generate a response.'),
        metadata={
            'model': ai_response.get('model'),
            'usage': ai_response.get('usage')
        }
    )
    
    # Update conversation timestamp
    from app.models.chat import Conversation
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db.commit()
    
    return {
        "conversation_id": conversation_id,
        "message": ai_response.get('response'),
        "model": ai_response.get('model'),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/chat/recommend")
async def get_ai_recommendations(
    query: str,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered recommendations with natural language reasoning.
    
    Example:
    - "I need something for a beach vacation"
    - "What's trending for fall?"
    - "Recommend formal wear for interview"
    
    The AI will:
    1. Understand your query
    2. Get relevant recommendations
    3. Explain why each item suits you
    4. Provide styling suggestions
    """
    from app.services.ai_fashion_chat_service import get_ai_fashion_chat_service
    
    chat_service = get_ai_fashion_chat_service()
    
    # Get AI-powered recommendations
    result = chat_service.get_recommendations_with_reasoning(
        user_id=current_user.id,
        user_query=query,
        db=db
    )
    
    return result


@app.get("/api/v1/chat/conversations")
async def get_conversations(
    limit: int = 20,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat conversations."""
    from app.services.ai_fashion_chat_service import ConversationManager
    
    conv_manager = ConversationManager(db)
    conversations = conv_manager.get_user_conversations(
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "total": len(conversations),
        "conversations": conversations
    }


@app.get("/api/v1/chat/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full conversation history."""
    from app.services.ai_fashion_chat_service import ConversationManager
    from app.models.chat import Conversation
    
    # Verify ownership
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv_manager = ConversationManager(db)
    messages = conv_manager.get_conversation_history(conversation_id)
    
    return {
        "conversation_id": conversation_id,
        "title": conversation.title,
        "messages": messages,
        "total_messages": len(messages)
    }


@app.delete("/api/v1/chat/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation."""
    from app.models.chat import Conversation
    
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        .first()
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"status": "success", "message": "Conversation deleted"}


# ============================================
# SIZE RECOMMENDATION ENDPOINTS
# ============================================

@app.post("/api/v1/size/recommend")
async def recommend_size(
    image: UploadFile = File(...),
    garment_type: str = "shirt",
    gender: str = "unisex",
    user_height_cm: Optional[float] = None,
    current_user: user_model.User = Depends(get_current_user)
):
    """Get size recommendation from image"""
    # Save image
    temp_path = f"temp/size_{uuid.uuid4()}.png"
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    
    # Estimate measurements
    measurements = size_service.estimate_measurements_from_image(
        temp_path,
        user_height_cm or current_user.height_cm
    )
    
    # Get recommendation
    recommendation = size_service.recommend_size(
        measurements,
        garment_type,
        gender
    )
    
    # Clean up
    os.remove(temp_path)
    
    return recommendation


# ============================================
# SOCIAL ENDPOINTS
# ============================================

@app.post("/api/v1/posts")
async def create_post(
    caption: Optional[str] = None,
    image: UploadFile = File(...),
    tryon_id: Optional[int] = None,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a post"""
    post_id = str(uuid.uuid4())
    image_path = f"uploads/posts/{post_id}.png"
    
    os.makedirs("uploads/posts", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(await image.read())
    
    post = social_model.Post(
        user_id=current_user.id,
        caption=caption,
        image_url=image_path,
        tryon_id=tryon_id
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {"id": post.id, "message": "Post created"}


@app.get("/api/v1/feed")
async def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get social feed"""
    posts = db.query(social_model.Post).filter(
        social_model.Post.is_public == True
    ).order_by(social_model.Post.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": len(posts), "posts": posts}


@app.post("/api/v1/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    # Check if already liked
    existing_like = db.query(social_model.Like).filter(
        social_model.Like.post_id == post_id,
        social_model.Like.user_id == current_user.id
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        db.commit()
        return {"liked": False}
    
    like = social_model.Like(
        user_id=current_user.id,
        item_type="post",
        item_id=post_id,
        post_id=post_id
    )
    
    db.add(like)
    db.commit()
    
    return {"liked": True}


@app.post("/api/v1/users/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: user_model.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing = db.query(social_model.Follow).filter(
        social_model.Follow.follower_id == current_user.id,
        social_model.Follow.followed_id == user_id
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
        return {"following": False}
    
    follow = social_model.Follow(
        follower_id=current_user.id,
        followed_id=user_id
    )
    
    db.add(follow)
    db.commit()
    
    return {"following": True}


# ============================================
# HEALTH & INFO
# ============================================

@app.get("/")
async def root():
    return {
        "name": "Virtue Try-On Complete API",
        "version": "2.0.0",
        "features": [
            "Authentication",
            "Virtual Try-On",
            "Try-On History & Favorites",
            "Virtual Wardrobe",
            "Size Recommendations",
            "Social Features",
            "Shopping Integration"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
