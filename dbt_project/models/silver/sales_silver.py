import duckdb
import os
from deltalake import write_deltalake

os.environ["AWS_ALLOW_HTTP"] = "true"

def model(dbt, session):
    dbt.config(materialized="table")
    
    df = session.sql("""
        SELECT
            id,
            customer,
            amount,
            date,
            CURRENT_TIMESTAMP as _processed_at
        FROM read_parquet('s3://lakehouse/bronze/sales_raw.parquet')
        WHERE amount > 0
    """).arrow()
    
    storage_options = {
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        "AWS_ALLOW_HTTP": "true",
        "AWS_ENDPOINT_URL": "http://minio:9000",
        "AWS_ACCESS_KEY_ID": "admin",
        "AWS_SECRET_ACCESS_KEY": "password123",
        "AWS_REGION": "us-east-1",
    }
    
    write_deltalake(
        "s3://lakehouse/silver/sales_silver",
        df,
        mode="overwrite",
        storage_options=storage_options
    )
    
    session.sql("""
        CREATE SECRET IF NOT EXISTS minio_s3 (
            TYPE S3,
            KEY_ID 'admin',
            SECRET 'password123',
            REGION 'us-east-1',
            ENDPOINT 'minio:9000',
            URL_STYLE 'path',
            USE_SSL false
        );
    """)
    
    return session.sql("SELECT * FROM delta_scan('s3://lakehouse/silver/sales_silver')")
