"""
Product schemas for API requests and responses
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base product schema"""
    name: str
    description: Optional[str] = None
    price: float
    brand: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    gender: str
    sizes: Optional[List[str]] = None
    colors: Optional[List[Dict[str, Any]]] = None
    images: List[str]
    main_image_url: str
    stock_quantity: int = 0


class ProductCreate(ProductBase):
    """Product creation schema"""
    pass


class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    gender: Optional[str] = None
    sizes: Optional[List[str]] = None
    colors: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[str]] = None
    main_image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductInDB(ProductBase):
    """Product in database schema"""
    id: int
    is_active: bool
    rating: float
    review_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Product(ProductInDB):
    """Product response schema"""
    pass


class ProductSearch(BaseModel):
    """Product search schema"""
    query: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "created_at"  # created_at, price, rating, name
    sort_order: Optional[str] = "desc"  # asc, desc
    page: int = 1
    limit: int = 20


class ProductListResponse(BaseModel):
    """Product list response schema"""
    products: List[Product]
    total: int
    page: int
    limit: int
    total_pages: int


class UserFavoriteCreate(BaseModel):
    """User favorite creation schema"""
    product_id: int


class UserFavorite(UserFavoriteCreate):
    """User favorite response schema"""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
