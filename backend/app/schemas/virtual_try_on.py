"""
Virtual Try-On schemas for API requests and responses
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class VirtualTryOnBase(BaseModel):
    """Base virtual try-on schema"""
    product_id: int
    person_image_url: str
    clothing_image_url: str


class VirtualTryOnCreate(VirtualTryOnBase):
    """Virtual try-on creation schema"""
    pass


class VirtualTryOnUpdate(BaseModel):
    """Virtual try-on update schema"""
    status: Optional[str] = None
    result_image_url: Optional[str] = None
    processing_time: Optional[float] = None
    model_version: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    error_message: Optional[str] = None


class VirtualTryOnInDB(VirtualTryOnBase):
    """Virtual try-on in database schema"""
    id: int
    user_id: int
    result_image_url: Optional[str] = None
    status: str
    processing_time: Optional[float] = None
    model_version: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VirtualTryOn(VirtualTryOnInDB):
    """Virtual try-on response schema"""
    pass


class VirtualTryOnRequest(BaseModel):
    """Virtual try-on request schema"""
    product_id: int
    person_image: str  # Base64 encoded image
    clothing_image: Optional[str] = None  # Base64 encoded image, if not provided, uses product image


class VirtualTryOnResponse(BaseModel):
    """Virtual try-on response schema"""
    id: int
    status: str
    result_image_url: Optional[str] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    quality_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime


class VirtualTryOnStatus(BaseModel):
    """Virtual try-on status schema"""
    id: int
    status: str
    progress: Optional[int] = None  # 0-100
    message: Optional[str] = None
