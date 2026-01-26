"""
Virtual Try-On endpoints
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.virtual_try_on import (
    VirtualTryOn, VirtualTryOnCreate, VirtualTryOnRequest, 
    VirtualTryOnResponse, VirtualTryOnStatus
)
from app.models.virtual_try_on import VirtualTryOn as VirtualTryOnModel
from app.models.product import Product as ProductModel
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User
from app.services.clip_vton import clip_vton_model
from app.services.image_processing import image_processor
from app.core.exceptions import VirtualTryOnException, ImageProcessingException

router = APIRouter()


async def process_virtual_try_on(virtual_try_on_id: int, db: Session):
    """Background task to process virtual try-on"""
    try:
        # Get the virtual try-on record
        vt_record = db.query(VirtualTryOnModel).filter(VirtualTryOnModel.id == virtual_try_on_id).first()
        if not vt_record:
            return
        
        # Update status to processing
        vt_record.status = "processing"
        db.commit()
        
        # Get product details
        product = db.query(ProductModel).filter(ProductModel.id == vt_record.product_id).first()
        if not product:
            vt_record.status = "failed"
            vt_record.error_message = "Product not found"
            db.commit()
            return
        
        # Process images
        person_image = image_processor.base64_to_image(vt_record.person_image_url)
        clothing_image = image_processor.base64_to_image(vt_record.clothing_image_url)
        
        # Preprocess images
        person_image, clothing_image = image_processor.preprocess_for_vton(person_image, clothing_image)
        
        # Generate virtual try-on
        result = await clip_vton_model.generate_virtual_try_on(
            person_image=person_image,
            clothing_image=clothing_image,
            text_prompt=f"{product.name} {product.category}"
        )
        
        # Convert result to base64
        result_base64 = image_processor.image_to_base64(result["result_image"])
        
        # Update record with results
        vt_record.status = "completed"
        vt_record.result_image_url = result_base64
        vt_record.processing_time = result["processing_time"]
        vt_record.confidence_score = result["confidence_score"]
        vt_record.quality_score = result["quality_score"]
        vt_record.model_version = "clip-vton-1.0"
        
        db.commit()
        
    except Exception as e:
        # Update record with error
        vt_record = db.query(VirtualTryOnModel).filter(VirtualTryOnModel.id == virtual_try_on_id).first()
        if vt_record:
            vt_record.status = "failed"
            vt_record.error_message = str(e)
            db.commit()


@router.post("/", response_model=VirtualTryOnResponse)
async def create_virtual_try_on(
    request: VirtualTryOnRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new virtual try-on request"""
    try:
        # Get product
        product = db.query(ProductModel).filter(ProductModel.id == request.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Use product image if clothing image not provided
        clothing_image_url = request.clothing_image if request.clothing_image else product.main_image_url
        
        # Validate person image
        person_image = image_processor.base64_to_image(request.person_image)
        is_valid, message = image_processor.validate_image_for_vton(person_image)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=message
            )
        
        # Create virtual try-on record
        db_vt = VirtualTryOnModel(
            user_id=current_user.id,
            product_id=request.product_id,
            person_image_url=request.person_image,
            clothing_image_url=clothing_image_url,
            status="pending"
        )
        
        db.add(db_vt)
        db.commit()
        db.refresh(db_vt)
        
        # Start background processing
        background_tasks.add_task(process_virtual_try_on, db_vt.id, db)
        
        return VirtualTryOnResponse(
            id=db_vt.id,
            status=db_vt.status,
            result_image_url=db_vt.result_image_url,
            processing_time=db_vt.processing_time,
            confidence_score=db_vt.confidence_score,
            quality_score=db_vt.quality_score,
            error_message=db_vt.error_message,
            created_at=db_vt.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create virtual try-on: {str(e)}"
        )


@router.get("/{vt_id}", response_model=VirtualTryOnResponse)
async def get_virtual_try_on(
    vt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get virtual try-on result by ID"""
    vt_record = db.query(VirtualTryOnModel).filter(
        VirtualTryOnModel.id == vt_id,
        VirtualTryOnModel.user_id == current_user.id
    ).first()
    
    if not vt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual try-on not found"
        )
    
    return VirtualTryOnResponse(
        id=vt_record.id,
        status=vt_record.status,
        result_image_url=vt_record.result_image_url,
        processing_time=vt_record.processing_time,
        confidence_score=vt_record.confidence_score,
        quality_score=vt_record.quality_score,
        error_message=vt_record.error_message,
        created_at=vt_record.created_at
    )


@router.get("/", response_model=List[VirtualTryOnResponse])
async def get_user_virtual_try_ons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all virtual try-ons for current user"""
    vt_records = db.query(VirtualTryOnModel).filter(
        VirtualTryOnModel.user_id == current_user.id
    ).order_by(VirtualTryOnModel.created_at.desc()).all()
    
    return [
        VirtualTryOnResponse(
            id=vt.id,
            status=vt.status,
            result_image_url=vt.result_image_url,
            processing_time=vt.processing_time,
            confidence_score=vt.confidence_score,
            quality_score=vt.quality_score,
            error_message=vt.error_message,
            created_at=vt.created_at
        )
        for vt in vt_records
    ]


@router.get("/{vt_id}/status", response_model=VirtualTryOnStatus)
async def get_virtual_try_on_status(
    vt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get virtual try-on status"""
    vt_record = db.query(VirtualTryOnModel).filter(
        VirtualTryOnModel.id == vt_id,
        VirtualTryOnModel.user_id == current_user.id
    ).first()
    
    if not vt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual try-on not found"
        )
    
    # Calculate progress based on status
    progress = 0
    message = "Virtual try-on request created"
    
    if vt_record.status == "processing":
        progress = 50
        message = "Processing virtual try-on..."
    elif vt_record.status == "completed":
        progress = 100
        message = "Virtual try-on completed successfully"
    elif vt_record.status == "failed":
        progress = 0
        message = f"Virtual try-on failed: {vt_record.error_message or 'Unknown error'}"
    
    return VirtualTryOnStatus(
        id=vt_record.id,
        status=vt_record.status,
        progress=progress,
        message=message
    )


@router.delete("/{vt_id}")
async def delete_virtual_try_on(
    vt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete virtual try-on record"""
    vt_record = db.query(VirtualTryOnModel).filter(
        VirtualTryOnModel.id == vt_id,
        VirtualTryOnModel.user_id == current_user.id
    ).first()
    
    if not vt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Virtual try-on not found"
        )
    
    db.delete(vt_record)
    db.commit()
    
    return {"message": "Virtual try-on deleted successfully"}
