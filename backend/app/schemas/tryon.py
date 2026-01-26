from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TryonRequest(BaseModel):
    cloth_id: int

class TryonResponse(BaseModel):
    status: str
    output_url: str
    tryon_id: Optional[int] = None

class TryonResult(BaseModel):
    id: int
    user_id: int
    cloth_id: int
    input_photo: str
    output_photo: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TryonHistory(BaseModel):
    id: int
    cloth_name: str
    cloth_category: str
    cloth_image_url: str
    input_photo: str
    output_photo: str
    created_at: datetime
    
    class Config:
        from_attributes = True
