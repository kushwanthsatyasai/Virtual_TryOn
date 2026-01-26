"""
Try-On History Model
===================
Store all virtual try-on results
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class TryOnHistory(Base):
    __tablename__ = "tryon_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Images
    person_image_url = Column(String, nullable=False)
    cloth_image_url = Column(String, nullable=False)
    result_image_url = Column(String, nullable=False)
    comparison_image_url = Column(String, nullable=True)
    
    # Generation Details
    quality_preset = Column(String, default="balanced")  # fast, balanced, high
    processing_time = Column(Float, nullable=True)  # seconds
    denoise_steps = Column(Integer, nullable=True)
    
    # Metadata
    cloth_type = Column(String, nullable=True)  # shirt, dress, jacket, etc.
    cloth_color = Column(String, nullable=True)
    cloth_brand = Column(String, nullable=True)
    cloth_price = Column(Float, nullable=True)
    
    # User Actions
    is_favorite = Column(Boolean, default=False, index=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(String, nullable=True)  # User notes
    tags = Column(JSON, nullable=True)  # ["summer", "casual", "work"]
    
    # Shopping
    is_purchased = Column(Boolean, default=False)
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_url = Column(String, nullable=True)
    
    # Social
    is_public = Column(Boolean, default=False)  # Share publicly
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tryon_history")
    
    def __repr__(self):
        return f"<TryOnHistory {self.id} - User {self.user_id}>"
