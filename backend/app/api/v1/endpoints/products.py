"""
Product management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductSearch, ProductListResponse, UserFavorite, UserFavoriteCreate
from app.models.product import Product as ProductModel, UserFavorite as UserFavoriteModel
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def get_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Product category"),
    gender: Optional[str] = Query(None, description="Gender filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination"""
    query = db.query(ProductModel).filter(ProductModel.is_active == True)
    
    # Apply filters
    if q:
        query = query.filter(ProductModel.name.ilike(f"%{q}%"))
    
    if category:
        query = query.filter(ProductModel.category == category)
    
    if gender:
        query = query.filter(ProductModel.gender == gender)
    
    if brand:
        query = query.filter(ProductModel.brand == brand)
    
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    
    # Apply sorting
    if hasattr(ProductModel, sort_by):
        sort_column = getattr(ProductModel, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=Product)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)"""
    # In a real app, you'd check if user is admin
    db_product = ProductModel(**product_data.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product (admin only)"""
    # In a real app, you'd check if user is admin
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)"""
    # In a real app, you'd check if user is admin
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    db_product.is_active = False
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """Get list of available categories"""
    categories = db.query(ProductModel.category).filter(ProductModel.is_active == True).distinct().all()
    return [cat[0] for cat in categories]


@router.get("/brands/list")
async def get_brands(db: Session = Depends(get_db)):
    """Get list of available brands"""
    brands = db.query(ProductModel.brand).filter(
        ProductModel.is_active == True,
        ProductModel.brand.isnot(None)
    ).distinct().all()
    return [brand[0] for brand in brands]


# Favorites endpoints
@router.post("/favorites", response_model=UserFavorite)
async def add_to_favorites(
    favorite_data: UserFavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add product to user favorites"""
    # Check if product exists
    product = db.query(ProductModel).filter(ProductModel.id == favorite_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already favorited
    existing_favorite = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == current_user.id,
        UserFavoriteModel.product_id == favorite_data.product_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in favorites"
        )
    
    # Create favorite
    db_favorite = UserFavoriteModel(
        user_id=current_user.id,
        product_id=favorite_data.product_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    
    return db_favorite


@router.get("/favorites", response_model=List[UserFavorite])
async def get_user_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite products"""
    favorites = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == current_user.id
    ).all()
    
    return favorites


@router.delete("/favorites/{product_id}")
async def remove_from_favorites(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove product from user favorites"""
    favorite = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == current_user.id,
        UserFavoriteModel.product_id == product_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()
    
    return {"message": "Product removed from favorites"}
