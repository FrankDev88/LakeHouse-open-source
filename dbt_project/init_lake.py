import duckdb

con = duckdb.connect("/workspace/dbt_project/dbt_metadata.duckdb")

# La view sales_silver referencia my_lake, así que hay que attacharlo
con.execute("LOAD httpfs; LOAD ducklake;")
con.execute("""
    CREATE SECRET IF NOT EXISTS minio_secret (
        TYPE S3, KEY_ID 'admin', SECRET 'password123',
        REGION 'us-east-1', ENDPOINT 'minio:9000',
        URL_STYLE 'path', USE_SSL false
    );
""")
con.execute("""
    ATTACH 'ducklake:/workspace/dbt_project/retail_metadata.ducklake' AS my_lake 
    (DATA_PATH 's3://retail/raw/retail_raw');
""")

print("=== PRIMERAS 5 FILAS DE sales_silver ===")
print(con.execute("SELECT * FROM main_silver.sales_silver LIMIT 5;").df().to_string(index=False))

print("\n=== CONTEO ===")
print(con.execute("SELECT COUNT(*) as total FROM main_silver.sales_silver;").df().to_string(index=False))

con.close()