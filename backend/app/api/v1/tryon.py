from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import asyncio

from ...core.database import get_db
from ...core.security import get_current_user
from ...core.config import settings
from ...models.user import User
from ...models.cloth import Cloth
from ...models.tryon_result import TryonResult
from ...schemas.tryon import TryonResponse, TryonHistory
from ...services.ai_service import AIService

router = APIRouter()

@router.post("/tryon", response_model=TryonResponse)
async def create_tryon(
    cloth_id: int = Form(...),
    user_image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a try-on result using AI model."""
    
    # Validate cloth exists
    cloth = db.query(Cloth).filter(Cloth.id == cloth_id).first()
    if not cloth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloth not found"
        )
    
    # Validate user image
    if not user_image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User image must be an image file"
        )
    
    # Validate file size
    content = await user_image.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Save user image
    file_extension = user_image.filename.split(".")[-1]
    input_filename = f"input_{uuid.uuid4()}.{file_extension}"
    input_path = os.path.join(settings.UPLOAD_DIR, input_filename)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(input_path, "wb") as buffer:
        buffer.write(content)
    
    # Generate output filename
    output_filename = f"tryon_{uuid.uuid4()}.png"
    output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
    
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Get cloth image path (remove /static prefix for local path)
        cloth_image_path = cloth.image_url.replace("/static/", "static/")
        
        # Generate try-on result
        success = await ai_service.generate_tryon(
            user_image_path=input_path,
            cloth_image_path=cloth_image_path,
            output_path=output_path
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate try-on result"
            )
        
        # Save result to database
        db_result = TryonResult(
            user_id=current_user.id,
            cloth_id=cloth_id,
            input_photo=f"/static/uploads/{input_filename}",
            output_photo=f"/static/generated_outputs/{output_filename}"
        )
        
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        return TryonResponse(
            status="success",
            output_url=f"/static/generated_outputs/{output_filename}",
            tryon_id=db_result.id
        )
        
    except Exception as e:
        # Clean up files on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Try-on generation failed: {str(e)}"
        )

@router.get("/history", response_model=List[TryonHistory])
async def get_tryon_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's try-on history."""
    
    results = db.query(TryonResult, Cloth).join(
        Cloth, TryonResult.cloth_id == Cloth.id
    ).filter(
        TryonResult.user_id == current_user.id
    ).order_by(
        TryonResult.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    history = []
    for result, cloth in results:
        history.append(TryonHistory(
            id=result.id,
            cloth_name=cloth.name,
            cloth_category=cloth.category,
            cloth_image_url=cloth.image_url,
            input_photo=result.input_photo,
            output_photo=result.output_photo,
            created_at=result.created_at
        ))
    
    return history

@router.get("/result/{result_id}")
async def get_tryon_result(
    result_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific try-on result."""
    
    result = db.query(TryonResult).filter(
        TryonResult.id == result_id,
        TryonResult.user_id == current_user.id
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Try-on result not found"
        )
    
    return result
