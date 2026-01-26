"""
User Model with Authentication
==============================
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    # Basic Info
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Profile
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Body Measurements (for size recommendations)
    height_cm = Column(Float, nullable=True)  # Height in cm
    weight_kg = Column(Float, nullable=True)  # Weight in kg
    chest_cm = Column(Float, nullable=True)   # Chest circumference
    waist_cm = Column(Float, nullable=True)   # Waist circumference
    hip_cm = Column(Float, nullable=True)     # Hip circumference
    shoulder_width_cm = Column(Float, nullable=True)
    preferred_size = Column(String, nullable=True)  # S, M, L, XL, etc.
    
    # Style Preferences
    style_tags = Column(JSON, nullable=True)  # ["casual", "formal", "sporty"]
    favorite_colors = Column(JSON, nullable=True)  # ["blue", "black"]
    favorite_brands = Column(JSON, nullable=True)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tryon_history = relationship("TryOnHistory", back_populates="user", cascade="all, delete-orphan")
    wardrobe_items = relationship("WardrobeItem", back_populates="user", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    
    # Social relationships
    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    followers = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User {self.username}>"
