"""
Favorites Model
==============
Quick access to favorite try-ons and items
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # What is favorited
    item_type = Column(String, nullable=False, index=True)  # tryon, wardrobe_item, outfit
    item_id = Column(Integer, nullable=False, index=True)
    
    # Metadata
    notes = Column(String, nullable=True)
    category = Column(String, nullable=True)  # For organizing favorites
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    
    def __repr__(self):
        return f"<Favorite {self.item_type} {self.item_id}>"
