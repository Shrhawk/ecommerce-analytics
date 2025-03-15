import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from flytekit import task, workflow
import pandas as pd
import numpy as np

from app.core.config import settings
from app.etl.pipeline import ETLPipeline

# Configuration
DB_URL = settings.SQLALCHEMY_DATABASE_URI
DATA_DIR = "ecommerce_data"

@dataclass
class DataQualityMetrics:
    """Data quality metrics for monitoring."""
    total_records: int
    invalid_records: int
    missing_values: Dict[str, int]
    validation_errors: List[str]
    business_rule_violations: Dict[str, int]  # Changed from Any to Dict[str, int]

    def to_dict(self) -> Dict:
        """Convert the metrics to a dictionary format."""
        result = asdict(self)
        # Convert numpy values to native Python types
        if self.business_rule_violations:
            result['business_rule_violations'] = {
                k: int(v) if isinstance(v, np.integer) else v
                for k, v in self.business_rule_violations.items()
            }
        return result

@task
def validate_data_files() -> bool:
    """
    Validate that all required data files exist and check their basic structure.
    
    Returns:
        bool: True if all files exist and are valid
    """
    required_files = [
        "product_categories.csv",
        "products.csv",
        "customers.csv",
        "orders.csv",
        "order_items.csv"
    ]
    
    data_dir = Path(DATA_DIR)
    
    for file in required_files:
        file_path = data_dir / file
        if not file_path.exists():
            raise ValueError(f"Required file {file} not found")
            
    return True

def check_data_quality(table_name: str, df: pd.DataFrame) -> DataQualityMetrics:
    """Enhanced data quality checks with business rules."""
    total_records = int(len(df))
    missing_values = {k: int(v) for k, v in df.isnull().sum().to_dict().items()}
    validation_errors = []
    invalid_records = 0
    business_rule_violations = {}

    # Common validations
    if 'price' in df.columns:
        invalid_prices = int((df['price'] < 0).sum())
        business_rule_violations['negative_prices'] = invalid_prices

    if 'quantity' in df.columns:
        invalid_quantities = int((df['quantity'] <= 0).sum())
        business_rule_violations['invalid_quantities'] = invalid_quantities

    if 'discount' in df.columns:
        invalid_discounts = int(((df['discount'] < 0) | (df['discount'] > 1)).sum())
        business_rule_violations['invalid_discounts'] = invalid_discounts

    # Table-specific validations
    if table_name == 'orders':
        future_dates = int((df['order_date'] > datetime.datetime.now()).sum())
        business_rule_violations['future_dates'] = future_dates

    if table_name == 'customers':
        invalid_emails = int((~df['email'].str.contains('@')).sum())
        business_rule_violations['invalid_emails'] = invalid_emails

    return DataQualityMetrics(
        total_records=total_records,
        invalid_records=invalid_records,
        missing_values=missing_values,
        validation_errors=validation_errors,
        business_rule_violations=business_rule_violations
    )


@task
def get_last_processed_date() -> Optional[datetime.datetime]:
    """
    Get the last processed date for incremental loading.
    
    Returns:
        Optional[datetime.datetime]: Last processed date if available
    """
    pipeline = ETLPipeline(DB_URL, DATA_DIR)
    try:
        with pipeline.engine.connect() as conn:
            result = conn.execute("SELECT MAX(order_date) FROM orders")
            return result.scalar()
    except Exception:
        return None
    finally:
        pipeline.engine.dispose()


def process_data() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Process all data using the ETL pipeline.
    
    Returns:
        Dict[str, Dict[str, Dict[str, Any]]]: Contains both record counts and quality metrics for each table
    """
    pipeline = ETLPipeline(DB_URL, DATA_DIR)

    try:
        # Run the complete pipeline
        pipeline.run()

        # Initialize results structure
        results = {
            'data': {  # Add an outer 'data' key to match expected structure
                'record_counts': {},
                'quality_metrics': {}
            }
        }

        for table_name in ['categories', 'products', 'customers', 'orders', 'order_items']:
            if table_name in pipeline.dfs:
                # Record counts
                results['data']['record_counts'][table_name] = len(pipeline.dfs[table_name])

                # Quality metrics
                metrics = check_data_quality(
                    table_name=table_name,
                    df=pipeline.dfs[table_name]
                )
                # Convert metrics to dictionary format
                results['data']['quality_metrics'][table_name] = metrics.to_dict()

        return results

    finally:
        pipeline.engine.dispose()


def generate_report(
    record_counts: Dict[str, int],
    quality_metrics: Dict[str, Dict[str, Any]],
    start_time: datetime.datetime
) -> str:
    """
    Generate a comprehensive report of the ETL process.
    
    Args:
        record_counts: Number of records processed per table
        quality_metrics: Quality metrics per table
        start_time: When the pipeline started
        
    Returns:
        str: Report text
    """
    # Ensure both times are timezone-naive
    end_time = datetime.datetime.now().replace(tzinfo=None)
    start_time = start_time.replace(tzinfo=None)
    duration = end_time - start_time

    report = f"""
    ETL Pipeline Report
    ------------------
    Start Time: {start_time}
    End Time: {end_time}
    Duration: {duration}
    
    Records Processed:
    """

    for table, count in record_counts.items():
        report += f"- {table}: {count}\n"

    report += "\nData Quality Metrics:\n"

    for table, metrics_dict in quality_metrics.items():
        report += f"\n{table}:\n"
        report += f"  Total Records: {metrics_dict['total_records']}\n"
        report += f"  Invalid Records: {metrics_dict['invalid_records']}\n"
        report += f"  Missing Values: {metrics_dict['missing_values']}\n"
        if metrics_dict['validation_errors']:
            report += "  Validation Errors:\n"
            for error in metrics_dict['validation_errors']:
                report += f"    - {error}\n"
        if metrics_dict['business_rule_violations']:
            report += "  Business Rule Violations:\n"
            for rule, count in metrics_dict['business_rule_violations'].items():
                report += f"    - {rule}: {count}\n"

    return report

@workflow
def etl_workflow() -> str:
    """
    Main ETL workflow that handles incremental loading and monitoring.
    
    Returns:
        str: Report of the ETL process
    """
    # Record start time
    start_time = datetime.datetime.now()

    # Validate input files
    validate_data_files()

    # Get last processed date for incremental loading
    last_processed_date = get_last_processed_date()

    # Process data and collect metrics
    results = process_data()

    # Generate report
    report = generate_report(
        record_counts=results.get("data")['record_counts'],
        quality_metrics=results.get("data")['quality_metrics'],
        start_time=start_time
    )
    
    return report

if __name__ == "__main__":
    print(f"Workflow output: {etl_workflow()}") 