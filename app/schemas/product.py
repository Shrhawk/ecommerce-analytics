from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCategoryBase(BaseModel):
    """Base schema for product category data."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class ProductCategoryCreate(ProductCategoryBase):
    """Schema for creating a new product category."""
    pass


class ProductCategoryUpdate(ProductCategoryBase):
    """Schema for updating a product category."""
    name: Optional[str]


class ProductCategoryInDB(ProductCategoryBase):
    """Schema for product category data as stored in the database."""
    category_id: int
    created_at: str

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    """Base schema for product data."""
    name: str
    description: Optional[str] = None
    price: Decimal
    cost: Optional[Decimal] = None
    category_id: int
    sku: str
    inventory_count: int
    weight: Optional[Decimal] = None
    is_active: bool = True
    name_category: Optional[str] = None
    profit_margin: Optional[Decimal] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(ProductBase):
    """Schema for updating a product."""
    name: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    sku: Optional[str] = None
    inventory_count: Optional[int] = None
    name_category: Optional[str] = None
    profit_margin: Optional[Decimal] = None


class ProductInDB(ProductBase):
    """Schema for product data as stored in the database."""
    product_id: int
    created_at: str
    category: ProductCategoryInDB

    class Config:
        orm_mode = True 