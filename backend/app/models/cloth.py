from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base

class Cloth(Base):
    __tablename__ = "clothes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "shirt", "dress", "pants"
    image_url = Column(Text, nullable=False)  # Path to the clothing image
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="clothes")
    tryon_results = relationship("TryonResult", back_populates="cloth")
