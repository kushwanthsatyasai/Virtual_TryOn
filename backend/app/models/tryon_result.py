from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base

class TryonResult(Base):
    __tablename__ = "tryon_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cloth_id = Column(Integer, ForeignKey("clothes.id"), nullable=False)
    input_photo = Column(Text, nullable=False)  # Path to user's input photo
    output_photo = Column(Text, nullable=False)  # Path to generated try-on result
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tryon_results")
    cloth = relationship("Cloth", back_populates="tryon_results")
