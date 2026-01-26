from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import uuid
from typing import Optional

from ...core.database import get_db
from ...core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from ...core.config import settings
from ...models.user import User
from ...schemas.user import UserCreate, UserLogin, UserResponse, Token

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Register a new user with optional profile photo."""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Handle profile photo upload
    profile_photo_path = None
    if photo:
        # Validate file type
        if not photo.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Generate unique filename
        file_extension = photo.filename.split(".")[-1]
        filename = f"profile_{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await photo.read()
            buffer.write(content)
        
        profile_photo_path = f"/static/uploads/{filename}"
    
    # Create user
    hashed_password = get_password_hash(password)
    db_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        profile_photo=profile_photo_path
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    
    # Find user
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user
