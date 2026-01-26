"""
API v1 router configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, products, virtual_try_on, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(virtual_try_on.router, prefix="/virtual-try-on", tags=["virtual-try-on"])
