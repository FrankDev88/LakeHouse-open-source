import pandas as pd
from deltalake import DeltaTable
import os

def model(dbt, session):
    # dbt-duckdb provides the connection via 'session' (which is the duckdb connection)
    
    # Define storage options for deltalake
    storage_options = {
        "AWS_ENDPOINT_URL": os.getenv("S3_ENDPOINT", "http://minio:9000"),
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "admin"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "password123"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "AWS_ALLOW_HTTP": "true",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true"
    }
    
    # Read the delta table using deltalake library
    dt = DeltaTable("s3://retail/raw", storage_options=storage_options)
    
    # Convert to pandas (or pyarrow)
    df = dt.to_pandas()
    
    # Return the dataframe - dbt will handle writing it to the target
    return df
