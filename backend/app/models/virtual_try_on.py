"""
Virtual Try-On model and related schemas
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class VirtualTryOn(Base):
    """Virtual Try-On session model"""
    __tablename__ = "virtual_try_ons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Input images
    person_image_url = Column(Text, nullable=False)  # User's photo
    clothing_image_url = Column(Text, nullable=False)  # Product image
    
    # Generated result
    result_image_url = Column(Text, nullable=True)  # Virtual try-on result
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Processing metadata
    processing_time = Column(Float, nullable=True)  # Time taken in seconds
    model_version = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)  # Model parameters used
    
    # Quality metrics
    confidence_score = Column(Float, nullable=True)  # Model confidence
    quality_score = Column(Float, nullable=True)  # Result quality
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="virtual_try_ons")
    product = relationship("Product", back_populates="virtual_try_ons")
