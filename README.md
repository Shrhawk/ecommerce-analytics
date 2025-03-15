# E-commerce Analytics Platform

This project implements a data processing pipeline for an e-commerce analytics platform, featuring ETL processes, a GraphQL API, and workflow orchestration.

## Features

- ETL pipeline for processing large CSV datasets
- PostgreSQL database with optimized schema and partitioning
- FastAPI-based GraphQL API
- Flyte workflow orchestration
- Comprehensive data analytics capabilities
- Docker support for easy deployment

## Requirements

- Python 3.12.2
- PostgreSQL
- Docker and Docker Compose

## Docker Setup (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/Shrhawk/ecommerce-analytics.git
cd ecommerce-analytics
```

2. Copy the environment file:
```bash
cp example.env .env
```

3. Build and start the services:
```bash
docker-compose up --build
```

### Docker Commands

1. Run database migrations:
```bash
docker-compose run web alembic upgrade head
```

2. Generate sample data:
```bash
docker-compose run web python data-generator.py
```

3. Run ETL pipeline:
```bash
docker-compose run web python app/etl/pipeline.py
```

4. Run ETL workflow:
```bash
docker-compose run web python app/workflows/etl_workflow.py
```

Once you are done with above queries, you can access the API and Graphql playground.

The following services will be available:
- API Docs: http://localhost:8000/docs
- Graphql: http://localhost:8000/graphql

Copy Graphql queries and variables from `graphql_queries.md` and run in playground.
