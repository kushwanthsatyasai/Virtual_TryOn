from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from ...core.database import get_db
from ...core.security import get_current_user
from ...core.config import settings
from ...models.user import User
from ...models.cloth import Cloth
from ...schemas.cloth import ClothCreate, ClothResponse

router = APIRouter()

@router.post("/upload_cloth", response_model=ClothResponse)
async def upload_cloth(
    name: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new clothing image."""
    
    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size
    content = await image.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    file_extension = image.filename.split(".")[-1]
    filename = f"cloth_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Create cloth record
    db_cloth = Cloth(
        name=name,
        category=category,
        image_url=f"/static/uploads/{filename}",
        uploaded_by=current_user.id
    )
    
    db.add(db_cloth)
    db.commit()
    db.refresh(db_cloth)
    
    return db_cloth

@router.get("/clothes", response_model=List[ClothResponse])
async def get_clothes(
    category: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get list of available clothes, optionally filtered by category."""
    
    query = db.query(Cloth)
    
    if category:
        query = query.filter(Cloth.category == category)
    
    clothes = query.offset(offset).limit(limit).all()
    return clothes

@router.get("/clothes/{cloth_id}", response_model=ClothResponse)
async def get_cloth(
    cloth_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific cloth by ID."""
    
    cloth = db.query(Cloth).filter(Cloth.id == cloth_id).first()
    if not cloth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloth not found"
        )
    
    return cloth

@router.get("/my_clothes", response_model=List[ClothResponse])
async def get_my_clothes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get clothes uploaded by the current user."""
    
    clothes = db.query(Cloth).filter(Cloth.uploaded_by == current_user.id).all()
    return clothes
