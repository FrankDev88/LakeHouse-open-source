import pandas as pd
import duckdb
import os

def ingest_to_ducklake():
    # 1. Configuración de credenciales
    s3_endpoint = os.getenv("S3_ENDPOINT", "http://minio:9000")
    # DuckDB requiere el endpoint sin 'http://' para su configuración
    clean_endpoint = s3_endpoint.replace("http://", "").replace("https://", "")
    
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "admin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "password123")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    print(f"Iniciando configuración hacia {clean_endpoint}...")

    # 2. Conectar a DuckDB y configurar extensiones
    con = duckdb.connect()
    
    # Instalamos y cargamos la extensión de S3 y DuckLake
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    con.execute("INSTALL ducklake;")
    con.execute("LOAD ducklake;")

    # Creamos el secreto en DuckDB para apuntar a MinIO (reemplaza tu storage_options)
    # USE_SSL false y URL_STYLE 'path' equivalen al AWS_ALLOW_HTTP y compatibilidad MinIO
    con.execute(f"""
        CREATE SECRET minio_secret (
            TYPE S3,
            KEY_ID '{access_key}',
            SECRET '{secret_key}',
            REGION '{region}',
            ENDPOINT '{clean_endpoint}',
            URL_STYLE 'path',
            USE_SSL false
        );
    """)

    # 3. Leer el DataFrame desde tu archivo CSV
    print("Cargando el archivo warehouse.csv...")
    try:
        df = pd.read_csv("warehouse.csv")
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'warehouse.csv'.")
        return

    # 4. Escribir a DuckLake en el bucket 'retail'
    ducklake_path = "s3://retail/raw/retail_raw"
    print(f"Escribiendo a formato DuckLake en la ruta: {ducklake_path}...")
    
    # ATTACH crea el metastore (el 'cerebro' de DuckLake) y lo vincula a tu bucket en MinIO
    # Se creará un archivo local 'retail_metadata.ducklake' para gobernar esa ruta
    con.execute(f"""
        ATTACH 'ducklake:retail_metadata.ducklake' AS my_lake 
        (DATA_PATH '{ducklake_path}');
    """)
    
    # Escribimos los datos. 
    # Usar CREATE OR REPLACE TABLE equivale al mode="overwrite"
    # (Si quisieras mode="append", usarías INSERT INTO my_lake.warehouse SELECT * FROM df)
    con.execute("CREATE OR REPLACE TABLE my_lake.warehouse AS SELECT * FROM df;")
    
    print("¡Ingesta a DuckLake completada con éxito!")

if __name__ == "__main__":
    ingest_to_ducklake()