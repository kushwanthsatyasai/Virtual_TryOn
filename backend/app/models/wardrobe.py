"""
Virtual Closet Models
====================
Wardrobe items and outfit combinations
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

# Association table for outfit items
outfit_items = Table(
    'outfit_items',
    Base.metadata,
    Column('outfit_id', Integer, ForeignKey('outfits.id'), primary_key=True),
    Column('wardrobe_item_id', Integer, ForeignKey('wardrobe_items.id'), primary_key=True)
)

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)  # top, bottom, dress, shoes, accessories
    subcategory = Column(String, nullable=True)  # t-shirt, jeans, sneakers, etc.
    
    # Images
    image_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    
    # Details
    brand = Column(String, nullable=True)
    color = Column(String, nullable=True, index=True)
    pattern = Column(String, nullable=True)  # solid, striped, floral, etc.
    material = Column(String, nullable=True)  # cotton, denim, leather, etc.
    size = Column(String, nullable=True)
    
    # Attributes
    season = Column(JSON, nullable=True)  # ["spring", "summer"]
    occasion = Column(JSON, nullable=True)  # ["casual", "formal", "sport"]
    style_tags = Column(JSON, nullable=True)  # ["vintage", "modern", "minimalist"]
    
    # Shopping Info
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_price = Column(Float, nullable=True)
    purchase_url = Column(String, nullable=True)
    
    # Usage Stats
    times_worn = Column(Integer, default=0)
    last_worn = Column(DateTime(timezone=True), nullable=True)
    
    # User Actions
    is_favorite = Column(Boolean, default=False, index=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)  # Still own it?
    condition = Column(String, nullable=True)  # new, good, fair, worn
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wardrobe_items")
    outfits = relationship("Outfit", secondary=outfit_items, back_populates="items")
    
    def __repr__(self):
        return f"<WardrobeItem {self.name} ({self.category})>"


class Outfit(Base):
    __tablename__ = "outfits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic Info
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Image (generated composition)
    image_url = Column(String, nullable=True)
    
    # Attributes
    season = Column(JSON, nullable=True)
    occasion = Column(JSON, nullable=True)
    style_tags = Column(JSON, nullable=True)
    
    # Usage
    times_worn = Column(Integer, default=0)
    last_worn = Column(DateTime(timezone=True), nullable=True)
    
    # User Actions
    is_favorite = Column(Boolean, default=False, index=True)
    rating = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    
    # Social
    is_public = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="outfits")
    items = relationship("WardrobeItem", secondary=outfit_items, back_populates="outfits")
    
    def __repr__(self):
        return f"<Outfit {self.name}>"
