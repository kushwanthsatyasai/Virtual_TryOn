from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ClothBase(BaseModel):
    name: str
    category: str

class ClothCreate(ClothBase):
    pass

class ClothResponse(ClothBase):
    id: int
    image_url: str
    uploaded_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True
