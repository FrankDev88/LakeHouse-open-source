import duckdb
import os
from deltalake import write_deltalake

os.environ["AWS_ALLOW_HTTP"] = "true"

def model(dbt, session):
    dbt.config(materialized="table")
    
    silver_rel = dbt.ref('sales_silver')
    
    df = session.sql("""
        SELECT
            date,
            COUNT(id) as total_transactions,
            SUM(amount) as total_sales,
            CURRENT_TIMESTAMP as _processed_at
        FROM silver_rel
        GROUP BY date
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
        "s3://lakehouse/gold/sales_gold",
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
    
    return session.sql("SELECT * FROM delta_scan('s3://lakehouse/gold/sales_gold')")


# This part is user provided model code
# you will need to copy the next section to run the code
# COMMAND ----------
# this part is dbt logic for get ref work, do not modify

def ref(*args, **kwargs):
    refs = {"sales_silver": "\"lakehouse\".\"main\".\"sales_silver\""}
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
    identifier = "sales_gold"
    
    def __repr__(self):
        return '"lakehouse"."main"."sales_gold"'


class dbtObj:
    def __init__(self, load_df_function) -> None:
        self.source = lambda *args: source(*args, dbt_load_df_function=load_df_function)
        self.ref = lambda *args, **kwargs: ref(*args, **kwargs, dbt_load_df_function=load_df_function)
        self.config = config
        self.this = this()
        self.is_incremental = False

# COMMAND ----------


