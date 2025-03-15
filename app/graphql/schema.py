from datetime import datetime, date
from typing import List, Optional

import strawberry
from sqlalchemy import and_
from sqlalchemy.orm import Session
from strawberry.types import Info

from app.db.session import get_db
from app.models.ecommerce import Product as ProductModel
from app.models.ecommerce import ProductCategory as ProductCategoryModel
from app.models.ecommerce import Order as OrderModel
from app.models.ecommerce import OrderItem as OrderItemModel
from app.models.ecommerce import Customer as CustomerModel
from app.models.ecommerce import DailySalesAggregation as DailySalesAggregationModel


@strawberry.type
class ProductCategory:
    """GraphQL type for product categories."""
    category_id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    created_at: str

    @classmethod
    def from_db_model(cls, model: ProductCategoryModel) -> "ProductCategory":
        return cls(
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            created_at=model.created_at
        )


@strawberry.type
class Product:
    """GraphQL type for products."""
    product_id: int
    name: str
    description: Optional[str]
    price: float
    cost: Optional[float]
    category_id: int
    sku: str
    inventory_count: int
    weight: Optional[float]
    created_at: str
    is_active: bool
    name_category: Optional[str]
    profit_margin: Optional[float]
    category: Optional[ProductCategory]

    @classmethod
    def from_db_model(cls, model: ProductModel) -> "Product":
        return cls(
            product_id=model.product_id,
            name=model.name,
            description=model.description,
            price=model.price,
            cost=model.cost,
            category_id=model.category_id,
            sku=model.sku,
            inventory_count=model.inventory_count,
            weight=model.weight,
            created_at=model.created_at,
            is_active=model.is_active,
            name_category=model.name_category,
            profit_margin=model.profit_margin,
            category=ProductCategory.from_db_model(model.category) if model.category else None
        )


@strawberry.type
class Customer:
    """GraphQL type for customers."""
    customer_id: int
    email: str
    first_name: str
    last_name: str
    street_address: str
    city: str
    state: str
    zip_code: int
    country: str
    phone: str
    registration_date: str
    last_login: str
    total_orders: float
    lifetime_value: float
    first_order_date: Optional[datetime]
    last_order_date: Optional[datetime]
    average_order_value: Optional[float]
    days_between_orders: Optional[float]

    @classmethod
    def from_db_model(cls, model: CustomerModel) -> "Customer":
        return cls(
            customer_id=model.customer_id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            street_address=model.street_address,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            country=model.country,
            phone=model.phone,
            registration_date=model.registration_date,
            last_login=model.last_login,
            total_orders=model.total_orders,
            lifetime_value=model.lifetime_value,
            first_order_date=model.first_order_date,
            last_order_date=model.last_order_date,
            average_order_value=model.average_order_value,
            days_between_orders=model.days_between_orders
        )


@strawberry.type
class OrderItem:
    """GraphQL type for order items."""
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    discount: float
    total: float
    product: Product

    @classmethod
    def from_db_model(cls, model: OrderItemModel) -> "OrderItem":
        return cls(
            order_item_id=model.order_item_id,
            order_id=model.order_id,
            product_id=model.product_id,
            quantity=model.quantity,
            price=model.price,
            discount=model.discount,
            total=model.total,
            product=Product.from_db_model(model.product)
        )


@strawberry.type
class Order:
    """GraphQL type for orders."""
    order_id: int
    customer_id: int
    order_date: datetime
    status: str
    payment_method: str
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_zip: int
    shipping_country: str
    processing_date: Optional[datetime]
    shipping_date: Optional[datetime]
    delivery_date: Optional[datetime]
    total_amount: float
    total: float
    profit: float
    quantity: int
    customer: Customer
    order_items: List[OrderItem]

    @classmethod
    def from_db_model(cls, model: OrderModel) -> "Order":
        return cls(
            order_id=model.order_id,
            customer_id=model.customer_id,
            order_date=model.order_date,
            status=model.status,
            payment_method=model.payment_method,
            shipping_address=model.shipping_address,
            shipping_city=model.shipping_city,
            shipping_state=model.shipping_state,
            shipping_zip=model.shipping_zip,
            shipping_country=model.shipping_country,
            processing_date=model.processing_date,
            shipping_date=model.shipping_date,
            delivery_date=model.delivery_date,
            total_amount=model.total_amount,
            total=model.total,
            profit=model.profit,
            quantity=model.quantity,
            customer=Customer.from_db_model(model.customer),
            order_items=[OrderItem.from_db_model(item) for item in model.order_items]
        )


@strawberry.type
class DailySalesAggregation:
    """GraphQL type for daily sales aggregation."""
    order_date: datetime
    product_id: int
    category_id: int
    units_sold: int
    revenue: float
    order_count: int
    avg_unit_price: float
    product: Product
    category: ProductCategory

    @classmethod
    def from_db_model(cls, model: DailySalesAggregationModel) -> "DailySalesAggregation":
        return cls(
            order_date=model.order_date,
            product_id=model.product_id,
            category_id=model.category_id,
            units_sold=model.units_sold,
            revenue=model.revenue,
            order_count=model.order_count,
            avg_unit_price=model.avg_unit_price,
            product=Product.from_db_model(model.product),
            category=ProductCategory.from_db_model(model.category)
        )


@strawberry.type
class Query:
    """GraphQL query type."""

    @strawberry.field
    def product(self, info: Info, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        db: Session = next(get_db())
        try:
            product = db.query(ProductModel).get(product_id)
            return Product.from_db_model(product) if product else None
        finally:
            db.close()

    @strawberry.field
    def products(
        self,
        info: Info,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """Get a list of products with optional filtering."""
        db: Session = next(get_db())
        try:
            query = db.query(ProductModel)
            
            if category_id is not None:
                query = query.filter(ProductModel.category_id == category_id)
            if is_active is not None:
                query = query.filter(ProductModel.is_active == is_active)
            
            products = query.offset(skip).limit(limit).all()
            return [Product.from_db_model(p) for p in products]
        finally:
            db.close()

    @strawberry.field
    def category(self, info: Info, category_id: int) -> Optional[ProductCategory]:
        """Get a category by ID."""
        db: Session = next(get_db())
        try:
            category = db.query(ProductCategoryModel).get(category_id)
            return ProductCategory.from_db_model(category) if category else None
        finally:
            db.close()

    @strawberry.field
    def categories(
        self,
        info: Info,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
    ) -> List[ProductCategory]:
        """Get a list of categories with optional filtering."""
        db: Session = next(get_db())
        try:
            query = db.query(ProductCategoryModel)
            
            if parent_id is not None:
                query = query.filter(ProductCategoryModel.parent_id == parent_id)
            
            categories = query.offset(skip).limit(limit).all()
            return [ProductCategory.from_db_model(c) for c in categories]
        finally:
            db.close()

    @strawberry.field
    def order(self, info: Info, order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        db: Session = next(get_db())
        try:
            order = db.query(OrderModel).get(order_id)
            return Order.from_db_model(order) if order else None
        finally:
            db.close()

    @strawberry.field
    def customer(self, info: Info, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        db: Session = next(get_db())
        try:
            customer = db.query(CustomerModel).get(customer_id)
            return Customer.from_db_model(customer) if customer else None
        finally:
            db.close()

    @strawberry.field
    def daily_sales(
        self,
        info: Info,
        start_date: date,
        end_date: date,
        category_id: Optional[int] = None
    ) -> List[DailySalesAggregation]:
        """Get daily sales aggregation data."""
        db: Session = next(get_db())
        try:
            query = db.query(DailySalesAggregationModel).filter(
                and_(
                    DailySalesAggregationModel.order_date >= start_date,
                    DailySalesAggregationModel.order_date <= end_date
                )
            )
            
            if category_id is not None:
                query = query.filter(DailySalesAggregationModel.category_id == category_id)
            
            results = query.all()
            return [DailySalesAggregation.from_db_model(r) for r in results]
        finally:
            db.close()


schema = strawberry.Schema(query=Query)