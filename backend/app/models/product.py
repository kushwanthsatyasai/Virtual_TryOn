"""
Product model and related schemas
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    brand = Column(String(100), nullable=True)
    category = Column(String(100), nullable=False, index=True)
    subcategory = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=False, index=True)  # men, women, unisex
    sizes = Column(JSON, nullable=True)  # Available sizes
    colors = Column(JSON, nullable=True)  # Available colors
    images = Column(JSON, nullable=False)  # List of image URLs
    main_image_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    virtual_try_ons = relationship("VirtualTryOn", back_populates="product")
    favorites = relationship("UserFavorite", back_populates="product")


class UserFavorite(Base):
    """User favorites model"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")
