import logging
from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """ETL Pipeline for processing e-commerce data."""

    def __init__(self, db_url: str, data_dir: str):
        """
        Initialize ETL pipeline.

        Args:
            db_url: Database connection URL
            data_dir: Directory containing CSV files
        """
        self.engine = create_engine(db_url)
        self.data_dir = Path(data_dir)
        self.dfs: Dict[str, pd.DataFrame] = {}

    def extract(self) -> None:
        """Extract data from CSV files with validation."""
        try:
            logger.info("Starting data extraction...")

            # Read and validate product categories
            self.dfs['categories'] = self._read_and_validate_categories()

            # Read and validate products
            self.dfs['products'] = self._read_and_validate_products()

            # Read and validate customers
            self.dfs['customers'] = self._read_and_validate_customers()

            # Read and validate orders
            self.dfs['orders'] = self._read_and_validate_orders()

            # Read and validate order items
            self.dfs['order_items'] = self._read_and_validate_order_items()

            logger.info("Data extraction completed successfully")

        except Exception as e:
            logger.error(f"Error during data extraction: {str(e)}")
            raise

    def transform(self) -> None:
        """Apply all transformation rules to the data."""
        try:
            logger.info("Starting data transformation...")

            # 1. Join product information with categories
            self._transform_product_data()

            # 2. Calculate revenue per order
            self._calculate_order_revenue()

            # 3. Enrich customer data
            self._enrich_customer_data()

            # 4. Aggregate daily sales data
            self._aggregate_daily_sales()

            # 5. Generate time dimension
            self._generate_time_dimension()

            logger.info("Data transformation completed successfully")

        except Exception as e:
            logger.error(f"Error during data transformation: {str(e)}")
            raise

    def load(self) -> None:
        """Load transformed data into PostgreSQL using bulk operations."""
        try:
            logger.info("Starting data loading...")

            # Load dimension tables first
            self._load_dimension_tables()

            # Load fact tables
            self._load_fact_tables()

            logger.info("Data loading completed successfully")

        except Exception as e:
            logger.error(f"Error during data loading: {str(e)}")
            raise

    def _read_and_validate_categories(self) -> pd.DataFrame:
        """Read and validate product categories data."""
        df = pd.read_csv(self.data_dir / 'product_categories.csv')

        # Validate required columns
        required_cols = ['category_id', 'name', 'description', 'parent_id']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in product_categories.csv")

        # Clean data
        df['description'] = df['description'].fillna('')
        df['parent_id'] = pd.to_numeric(df['parent_id'], errors='coerce').astype('Int64')

        return df

    def _read_and_validate_products(self) -> pd.DataFrame:
        """Read and validate products data."""
        df = pd.read_csv(self.data_dir / 'products.csv')

        # Validate required columns
        required_cols = ['product_id', 'name', 'price', 'category_id', 'sku']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in products.csv")

        # Validate data types and constraints
        if df['price'].min() < 0:
            raise ValueError("Found negative prices in products data")

        # Clean data
        df['description'] = df['description'].fillna('')
        df['weight'] = df['weight'].fillna(0)
        df['is_active'] = df['is_active'].fillna(True)

        return df

    def _read_and_validate_customers(self) -> pd.DataFrame:
        """Read and validate customers data."""
        df = pd.read_csv(self.data_dir / 'customers.csv')

        # Validate required columns
        required_cols = ['customer_id', 'email', 'first_name', 'last_name']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in customers.csv")

        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        invalid_emails = ~df['email'].str.match(email_pattern)
        if invalid_emails.any():
            logger.warning(f"Found {invalid_emails.sum()} invalid email addresses")
            df.loc[invalid_emails, 'email'] = None

        return df

    def _read_and_validate_orders(self) -> pd.DataFrame:
        """Read and validate orders data."""
        df = pd.read_csv(self.data_dir / 'orders.csv')

        # Validate required columns
        required_cols = [
            'order_id', 'customer_id', 'order_date', 'status',
            'payment_method', 'total_amount'
        ]
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in orders.csv")

        # Convert dates to datetime
        date_columns = ['order_date', 'processing_date', 'shipping_date', 'delivery_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        # Validate order amounts
        if df['total_amount'].min() < 0:
            raise ValueError("Found negative order amounts")

        return df

    def _read_and_validate_order_items(self) -> pd.DataFrame:
        """Read and validate order items data."""
        df = pd.read_csv(self.data_dir / 'order_items.csv')

        # Validate required columns
        required_cols = [
            'order_item_id', 'order_id', 'product_id',
            'quantity', 'price', 'total'
        ]
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in order_items.csv")

        # Validate quantities and prices
        if df['quantity'].min() <= 0:
            raise ValueError("Found zero or negative quantities")
        if df['price'].min() < 0:
            raise ValueError("Found negative prices")

        return df

    def _transform_product_data(self) -> None:
        """Join product information with categories and add derived attributes."""
        products_df = self.dfs['products']
        categories_df = self.dfs['categories']

        # Join products with categories
        self.dfs['products'] = products_df.merge(
            categories_df[['category_id', 'name']],
            on='category_id',
            how='left',
            suffixes=('', '_category')
        )

        # Add profit margin calculation
        self.dfs['products']['profit_margin'] = (
                (self.dfs['products']['price'] - self.dfs['products']['cost']) /
                self.dfs['products']['price']
        ).round(4)

    def _calculate_order_revenue(self) -> None:
        """Calculate revenue and profit for each order."""
        orders_df = self.dfs['orders']
        items_df = self.dfs['order_items']
        products_df = self.dfs['products']

        # Calculate revenue and profit per item
        items_with_products = items_df.merge(
            products_df[['product_id', 'cost']],
            on='product_id',
            how='left'
        )

        items_with_products['profit'] = (
                items_with_products['total'] -
                (items_with_products['cost'] * items_with_products['quantity'])
        )

        # Aggregate by order
        order_metrics = items_with_products.groupby('order_id').agg({
            'total': 'sum',
            'profit': 'sum',
            'quantity': 'sum'
        }).reset_index()

        # Update orders dataframe
        self.dfs['orders'] = orders_df.merge(
            order_metrics,
            on='order_id',
            how='left',
            suffixes=('', '_calculated')
        )

    def _enrich_customer_data(self) -> None:
        """Add derived attributes to customer data."""
        customers_df = self.dfs['customers']
        orders_df = self.dfs['orders']

        # Calculate customer metrics
        customer_metrics = orders_df[
            orders_df['status'].isin(['Delivered', 'In Transit', 'Shipped'])
        ].groupby('customer_id').agg({
            'order_id': 'count',
            'total': 'sum',
            'order_date': ['min', 'max']
        }).reset_index()

        customer_metrics.columns = [
            'customer_id', 'total_orders', 'lifetime_value',
            'first_order_date', 'last_order_date'
        ]

        # Calculate average order value and days between orders
        customer_metrics['average_order_value'] = (
                customer_metrics['lifetime_value'] /
                customer_metrics['total_orders']
        )

        customer_metrics['days_between_orders'] = (
                (customer_metrics['last_order_date'] - customer_metrics['first_order_date']).dt.days /
                customer_metrics['total_orders']
        )

        # Update customers dataframe
        self.dfs['customers'] = customers_df.merge(
            customer_metrics,
            on='customer_id',
            how='left'
        )

    def _aggregate_daily_sales(self) -> None:
        """Create daily sales aggregation by product and category."""
        orders_df = self.dfs['orders']
        items_df = self.dfs['order_items']
        products_df = self.dfs['products']

        # Join all necessary tables
        daily_sales = items_df.merge(
            orders_df[['order_id', 'order_date', 'status']],
            on='order_id',
            how='left'
        ).merge(
            products_df[['product_id', 'category_id']],
            on='product_id',
            how='left'
        )

        # Filter out cancelled/returned orders
        daily_sales = daily_sales[
            ~daily_sales['status'].isin(['Cancelled', 'Returned'])
        ]

        # Aggregate by date, product, and category
        self.dfs['daily_sales'] = daily_sales.groupby([
            pd.Grouper(key='order_date', freq='D'),
            'product_id',
            'category_id'
        ]).agg({
            'quantity': 'sum',
            'total': 'sum',
            'order_id': 'nunique'
        }).reset_index()

        self.dfs['daily_sales'].rename(columns={
            'quantity': 'units_sold',
            'total': 'revenue',
            'order_id': 'order_count'
        }, inplace=True)

        # Calculate average unit price
        self.dfs['daily_sales']['avg_unit_price'] = (
                self.dfs['daily_sales']['revenue'] /
                self.dfs['daily_sales']['units_sold']
        )

    def _generate_time_dimension(self) -> None:
        """Generate time dimension table for analytics."""
        # Get date range from orders
        start_date = self.dfs['orders']['order_date'].min()
        end_date = self.dfs['orders']['order_date'].max()

        # Generate date range
        dates = pd.date_range(start_date, end_date, freq='D')

        # Create time dimension dataframe
        self.dfs['dim_time'] = pd.DataFrame({
            'date': dates,
            'day_of_week': dates.dayofweek,
            'day_of_month': dates.day,
            'day_of_year': dates.dayofyear,
            'week_of_year': dates.isocalendar().week,
            'month': dates.month,
            'month_name': dates.strftime('%B'),
            'quarter': dates.quarter,
            'year': dates.year,
            'is_weekend': dates.dayofweek.isin([5, 6]),
            'is_holiday': False  # Would need holiday calendar to set this properly
        })

    def _load_dimension_tables(self) -> None:
        """Load dimension tables into the database."""
        logger.info("Loading dimension tables...")

        # Load time dimension
        self._bulk_insert_df(
            'dim_time',
            self.dfs['dim_time'],
            if_exists='replace'
        )

        # Load product categories
        self._bulk_insert_df(
            'product_categories',
            self.dfs['categories'],
            if_exists='replace'
        )

        # Load products
        self._bulk_insert_df(
            'products',
            self.dfs['products'],
            if_exists='replace'
        )

        # Load customers
        self._bulk_insert_df(
            'customers',
            self.dfs['customers'],
            if_exists='replace'
        )

    def _load_fact_tables(self) -> None:
        """Load fact tables into the database."""
        logger.info("Loading fact tables...")

        # Load orders
        self._bulk_insert_df(
            'orders',
            self.dfs['orders'],
            if_exists='append'
        )

        # Load order items
        self._bulk_insert_df(
            'order_items',
            self.dfs['order_items'],
            if_exists='append'
        )

        # Load daily sales aggregation
        self._bulk_insert_df(
            'daily_sales_aggregation',
            self.dfs['daily_sales'],
            if_exists='append'
        )

    def _bulk_insert_df(
            self,
            table_name: str,
            df: pd.DataFrame,
            if_exists: str = 'append',
            chunk_size: int = 10000
    ) -> None:
        """
        Efficiently insert a DataFrame into PostgreSQL using bulk operations.

        Args:
            table_name: Target table name
            df: DataFrame to insert
            if_exists: How to behave if table exists ('fail', 'replace', 'append')
            chunk_size: Number of rows per chunk for bulk insert
        """
        try:
            logger.info(f"Bulk inserting {len(df)} rows into {table_name}")

            df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=chunk_size
            )

            logger.info(f"Successfully loaded data into {table_name}")

        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {str(e)}")
            raise

    def run(self) -> None:
        """Run the complete ETL pipeline."""
        try:
            logger.info("Starting ETL pipeline...")

            self.extract()
            self.transform()
            self.load()

            logger.info("ETL pipeline completed successfully")

        except Exception as e:
            logger.error(f"ETL pipeline failed: {str(e)}")
            raise
        finally:
            self.engine.dispose()


def main():
    """Main entry point for the ETL pipeline."""
    # Configure database connection
    db_url = settings.SQLALCHEMY_DATABASE_URI
    data_dir = "ecommerce_data"

    try:
        # Initialize and run pipeline
        pipeline = ETLPipeline(db_url, data_dir)
        pipeline.run()

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
