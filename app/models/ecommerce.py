from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DimTime(Base):
    __tablename__ = 'dim_time'

    date = Column(DateTime, primary_key=True)
    day_of_week = Column(Integer)
    day_of_month = Column(Integer)
    day_of_year = Column(Integer)
    week_of_year = Column(BigInteger)
    month = Column(Integer)
    month_name = Column(String)
    quarter = Column(Integer)
    year = Column(Integer)
    is_weekend = Column(Boolean)
    is_holiday = Column(Boolean)

class ProductCategory(Base):
    __tablename__ = 'product_categories'

    category_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    description = Column(String)
    parent_id = Column(BigInteger, ForeignKey('product_categories.category_id'))
    created_at = Column(String)

    # Self-referential relationship for parent categories
    parent = relationship("ProductCategory", remote_side=[category_id])
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    cost = Column(Float)
    category_id = Column(BigInteger, ForeignKey('product_categories.category_id'))
    sku = Column(String)
    inventory_count = Column(BigInteger)
    weight = Column(Float)
    created_at = Column(String)
    is_active = Column(Boolean)
    name_category = Column(String)
    profit_margin = Column(Float)

    category = relationship("ProductCategory", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(BigInteger, primary_key=True)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(BigInteger)
    country = Column(String)
    phone = Column(String)
    registration_date = Column(String)
    last_login = Column(String)
    total_orders = Column(Float)
    lifetime_value = Column(Float)
    first_order_date = Column(DateTime)
    last_order_date = Column(DateTime)
    average_order_value = Column(Float)
    days_between_orders = Column(Float)

    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey('customers.customer_id'))
    order_date = Column(DateTime)
    status = Column(String)
    payment_method = Column(String)
    shipping_address = Column(String)
    shipping_city = Column(String)
    shipping_state = Column(String)
    shipping_zip = Column(BigInteger)
    shipping_country = Column(String)
    processing_date = Column(DateTime)
    shipping_date = Column(DateTime)
    delivery_date = Column(DateTime)
    total_amount = Column(Float)
    total = Column(Float)
    profit = Column(Float)
    quantity = Column(BigInteger)

    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey('orders.order_id'))
    product_id = Column(BigInteger, ForeignKey('products.product_id'))
    quantity = Column(BigInteger)
    price = Column(Float)
    discount = Column(Float)
    total = Column(Float)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class DailySalesAggregation(Base):
    __tablename__ = 'daily_sales_aggregation'

    order_date = Column(DateTime, primary_key=True)
    product_id = Column(BigInteger, ForeignKey('products.product_id'), primary_key=True)
    category_id = Column(BigInteger, ForeignKey('product_categories.category_id'))
    units_sold = Column(BigInteger)
    revenue = Column(Float)
    order_count = Column(BigInteger)
    avg_unit_price = Column(Float)

    product = relationship("Product")
    category = relationship("ProductCategory") 