import pandas as pd
import duckdb
import os
import datetime

def ingest():
    # Configuration
    s3_endpoint = os.getenv("S3_ENDPOINT", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "admin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "password123")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    print(f"Starting ingestion to {s3_endpoint}...")

    # Create dummy data
    data = {
        'id': range(1, 11),
        'customer': ['Customer A', 'Customer B', 'Customer C', 'Customer A', 'Customer B', 'Customer C', 'Customer A', 'Customer B', 'Customer C', 'Customer A'],
        'amount': [100.5, 200.0, 150.75, 300.2, 50.0, 120.5, 400.0, 250.25, 90.0, 500.0],
        'date': [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
    }
    df = pd.DataFrame(data)

    # Initialize DuckDB
    con = duckdb.connect()
    
    # Configure S3 access in DuckDB
    con.execute(f"""
        INSTALL httpfs;
        LOAD httpfs;
        SET s3_endpoint='{s3_endpoint.replace("http://", "")}';
        SET s3_access_key_id='{access_key}';
        SET s3_secret_access_key='{secret_key}';
        SET s3_region='{region}';
        SET s3_use_ssl=false;
        SET s3_url_style='path';
    """)

    # Write to S3 as Parquet
    print("Writing sales_raw.parquet to Bronze layer...")
    con.execute("COPY df TO 's3://lakehouse/bronze/sales_raw.parquet' (FORMAT PARQUET);")
    print("Ingestion completed successfully.")

if __name__ == "__main__":
    ingest()
