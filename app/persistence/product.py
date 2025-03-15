from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.ecommerce import Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductCategoryCreate, ProductCategoryUpdate


class ProductRepository:
    """Repository for product-related database operations."""

    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[Product]:
        """
        Get a product by ID.
        
        Args:
            db: Database session
            product_id: ID of the product to retrieve
            
        Returns:
            Optional[Product]: The product if found, None otherwise
        """
        return db.query(Product).filter(Product.product_id == product_id).first()

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Product], int]:
        """
        Get a list of products with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_id: Optional category ID to filter by
            is_active: Optional active status to filter by
            
        Returns:
            Tuple[List[Product], int]: List of products and total count
        """
        query = db.query(Product)
        
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
            
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return products, total

    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """
        Create a new product.
        
        Args:
            db: Database session
            product: Product data
            
        Returns:
            Product: The created product
        """
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product: ProductUpdate
    ) -> Optional[Product]:
        """
        Update a product.
        
        Args:
            db: Database session
            product_id: ID of the product to update
            product: Updated product data
            
        Returns:
            Optional[Product]: The updated product if found, None otherwise
        """
        db_product = ProductRepository.get_product(db, product_id)
        if not db_product:
            return None
            
        update_data = product.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
            
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        Delete a product.
        
        Args:
            db: Database session
            product_id: ID of the product to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_product = ProductRepository.get_product(db, product_id)
        if not db_product:
            return False
            
        db.delete(db_product)
        db.commit()
        return True


class ProductCategoryRepository:
    """Repository for product category-related database operations."""

    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[ProductCategory]:
        """
        Get a category by ID.
        
        Args:
            db: Database session
            category_id: ID of the category to retrieve
            
        Returns:
            Optional[ProductCategory]: The category if found, None otherwise
        """
        return db.query(ProductCategory).filter(ProductCategory.category_id == category_id).first()

    @staticmethod
    def get_categories(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
    ) -> Tuple[List[ProductCategory], int]:
        """
        Get a list of categories with optional filtering.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            parent_id: Optional parent category ID to filter by
            
        Returns:
            Tuple[List[ProductCategory], int]: List of categories and total count
        """
        query = db.query(ProductCategory)
        
        if parent_id is not None:
            query = query.filter(ProductCategory.parent_id == parent_id)
            
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        
        return categories, total

    @staticmethod
    def create_category(db: Session, category: ProductCategoryCreate) -> ProductCategory:
        """
        Create a new category.
        
        Args:
            db: Database session
            category: Category data
            
        Returns:
            ProductCategory: The created category
        """
        db_category = ProductCategory(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        category: ProductCategoryUpdate
    ) -> Optional[ProductCategory]:
        """
        Update a category.
        
        Args:
            db: Database session
            category_id: ID of the category to update
            category: Updated category data
            
        Returns:
            Optional[ProductCategory]: The updated category if found, None otherwise
        """
        db_category = ProductCategoryRepository.get_category(db, category_id)
        if not db_category:
            return None
            
        update_data = category.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
            
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """
        Delete a category.
        
        Args:
            db: Database session
            category_id: ID of the category to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        db_category = ProductCategoryRepository.get_category(db, category_id)
        if not db_category:
            return False
            
        # Check if category has products or child categories
        if db_category.products or db_category.children:
            return False
            
        db.delete(db_category)
        db.commit()
        return True 