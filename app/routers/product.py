from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.persistence.product import ProductRepository, ProductCategoryRepository
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductInDB,
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryInDB
)

router = APIRouter()


@router.get("/products/{product_id}", response_model=ProductInDB)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> ProductInDB:
    """
    Get a product by ID.
    
    Args:
        product_id: ID of the product to retrieve
        db: Database session
        
    Returns:
        ProductInDB: The product data
    """
    return ProductRepository.get_product(db, product_id)


@router.get("/products", response_model=List[ProductInDB])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
) -> List[ProductInDB]:
    """
    Get a list of products with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        category_id: Optional category ID to filter by
        is_active: Optional active status to filter by
        db: Database session
        
    Returns:
        List[ProductInDB]: List of products
    """
    products, _ = ProductRepository.get_products(
        db, skip, limit, category_id, is_active
    )
    return products


@router.post("/products", response_model=ProductInDB)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
) -> ProductInDB:
    """
    Create a new product.
    
    Args:
        product: Product data
        db: Database session
        
    Returns:
        ProductInDB: The created product
    """
    return ProductRepository.create_product(db, product)


@router.put("/products/{product_id}", response_model=ProductInDB)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
) -> ProductInDB:
    """
    Update a product.
    
    Args:
        product_id: ID of the product to update
        product: Updated product data
        db: Database session
        
    Returns:
        ProductInDB: The updated product
    """
    return ProductRepository.update_product(db, product_id, product)


@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a product.
    
    Args:
        product_id: ID of the product to delete
        db: Database session
    """
    ProductRepository.delete_product(db, product_id)


@router.get("/categories/{category_id}", response_model=ProductCategoryInDB)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> ProductCategoryInDB:
    """
    Get a category by ID.
    
    Args:
        category_id: ID of the category to retrieve
        db: Database session
        
    Returns:
        ProductCategoryInDB: The category data
    """
    return ProductCategoryRepository.get_category(db, category_id)


@router.get("/categories", response_model=List[ProductCategoryInDB])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> List[ProductCategoryInDB]:
    """
    Get a list of categories with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        parent_id: Optional parent category ID to filter by
        db: Database session
        
    Returns:
        List[ProductCategoryInDB]: List of categories
    """
    categories, _ = ProductCategoryRepository.get_categories(
        db, skip, limit, parent_id
    )
    return categories


@router.post("/categories", response_model=ProductCategoryInDB)
def create_category(
    category: ProductCategoryCreate,
    db: Session = Depends(get_db)
) -> ProductCategoryInDB:
    """
    Create a new category.
    
    Args:
        category: Category data
        db: Database session
        
    Returns:
        ProductCategoryInDB: The created category
    """
    return ProductCategoryRepository.create_category(db, category)


@router.put("/categories/{category_id}", response_model=ProductCategoryInDB)
def update_category(
    category_id: int,
    category: ProductCategoryUpdate,
    db: Session = Depends(get_db)
) -> ProductCategoryInDB:
    """
    Update a category.
    
    Args:
        category_id: ID of the category to update
        category: Updated category data
        db: Database session
        
    Returns:
        ProductCategoryInDB: The updated category
    """
    return ProductCategoryRepository.update_category(db, category_id, category)


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a category.
    
    Args:
        category_id: ID of the category to delete
        db: Database session
    """
    ProductCategoryRepository.delete_category(db, category_id) 