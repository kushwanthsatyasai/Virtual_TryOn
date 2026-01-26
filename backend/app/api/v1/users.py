from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...schemas.user import UserResponse

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    
    if name:
        current_user.name = name
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
