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


# This part is user provided model code
# you will need to copy the next section to run the code
# COMMAND ----------
# this part is dbt logic for get ref work, do not modify

def ref(*args, **kwargs):
    refs = {}
    key = '.'.join(args)
    version = kwargs.get("v") or kwargs.get("version")
    if version:
        key += f".v{version}"
    dbt_load_df_function = kwargs.get("dbt_load_df_function")
    return dbt_load_df_function(refs[key])


def source(*args, dbt_load_df_function):
    sources = {}
    key = '.'.join(args)
    return dbt_load_df_function(sources[key])


config_dict = {}


class config:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def get(key, default=None):
        return config_dict.get(key, default)

class this:
    """dbt.this() or dbt.this.identifier"""
    database = "lakehouse"
    schema = "main"
    identifier = "silver_warehouse"
    
    def __repr__(self):
        return '"lakehouse"."main"."silver_warehouse"'


class dbtObj:
    def __init__(self, load_df_function) -> None:
        self.source = lambda *args: source(*args, dbt_load_df_function=load_df_function)
        self.ref = lambda *args, **kwargs: ref(*args, **kwargs, dbt_load_df_function=load_df_function)
        self.config = config
        self.this = this()
        self.is_incremental = False

# COMMAND ----------


