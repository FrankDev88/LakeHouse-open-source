
  
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
        overwrite_schema=True,
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
    identifier = "sales_silver"
    
    def __repr__(self):
        return '"lakehouse"."main"."sales_silver"'


class dbtObj:
    def __init__(self, load_df_function) -> None:
        self.source = lambda *args: source(*args, dbt_load_df_function=load_df_function)
        self.ref = lambda *args, **kwargs: ref(*args, **kwargs, dbt_load_df_function=load_df_function)
        self.config = config
        self.this = this()
        self.is_incremental = False

# COMMAND ----------




def materialize(df, con):
    try:
        import pyarrow
        pyarrow_available = True
    except ImportError:
        pyarrow_available = False
    finally:
        if pyarrow_available and isinstance(df, pyarrow.Table):
            # https://github.com/duckdb/duckdb/issues/6584
            import pyarrow.dataset
    con.execute('create table "lakehouse"."main"."sales_silver__dbt_tmp" as select * from df')

  