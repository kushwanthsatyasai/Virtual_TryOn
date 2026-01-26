"""
Recommendation Models
====================
Database models for tracking recommendations and user interactions
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class RecommendationInteraction(Base):
    """Track user interactions with recommendations for ML improvement"""
    __tablename__ = "recommendation_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(String(255), nullable=False)
    
    # Recommendation context
    recommendation_score = Column(Float)
    recommendation_reason = Column(String(255))
    recommendation_algorithm = Column(String(100))  # e.g., 'content_based', 'collaborative'
    
    # User interaction
    interaction_type = Column(String(50), nullable=False)  # view, click, try, favorite, purchase, ignore
    interaction_data = Column(JSON)  # Additional data
    
    # Timestamps
    recommended_at = Column(DateTime, default=datetime.utcnow)
    interacted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="recommendation_interactions")
    
    # Indexes for query optimization
    __table_args__ = (
        Index('idx_user_item', 'user_id', 'item_id'),
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_recommended_at', 'recommended_at'),
    )


class UserStyleProfile(Base):
    """Store user's style profile for faster recommendations"""
    __tablename__ = "user_style_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Style preferences (JSON)
    favorite_categories = Column(JSON)  # {category: count}
    favorite_colors = Column(JSON)      # {color: count}
    favorite_brands = Column(JSON)      # {brand: count}
    favorite_styles = Column(JSON)      # {style: count}
    
    # Price preferences
    average_price_preference = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    
    # Activity stats
    total_tryons = Column(Integer, default=0)
    total_favorites = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    
    # Profile metadata
    profile_data = Column(JSON)  # Additional profile information
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="style_profile", uselist=False)


class RecommendationCache(Base):
    """Cache recommendations for performance"""
    __tablename__ = "recommendation_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Cached recommendations
    recommendations = Column(JSON)  # List of recommended items with scores
    category_filter = Column(String(100))  # Category filter used
    
    # Cache metadata
    algorithm_version = Column(String(50))
    cache_key = Column(String(255), unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When to invalidate cache
    
    # Relationship
    user = relationship("User", backref="recommendation_cache")
    
    # Indexes
    __table_args__ = (
        Index('idx_cache_expiry', 'user_id', 'expires_at'),
    )
