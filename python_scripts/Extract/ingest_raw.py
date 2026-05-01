import pandas as pd
from deltalake import write_deltalake
import os

def ingest_to_delta():
    # 1. Configuración de credenciales (extraídas de tu código original)
    s3_endpoint = os.getenv("S3_ENDPOINT", "http://minio:9000")
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "admin")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "password123")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    print(f"Iniciando configuración hacia {s3_endpoint}...")

    # 2. Diccionario de configuración para MinIO/S3
    # La configuración "AWS_S3_ALLOW_UNSAFE_RENAME" es importante cuando se usa MinIO 
    # u otros sistemas de almacenamiento compatibles con S3 que no bloquean archivos.
    storage_options = {
        "AWS_ENDPOINT_URL": s3_endpoint,
        "AWS_ACCESS_KEY_ID": access_key,
        "AWS_SECRET_ACCESS_KEY": secret_key,
        "AWS_REGION": region,
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true" ,
        "AWS_ALLOW_HTTP": "true"  # <--- Agrega esta línea
    }

    # 3. Leer el DataFrame desde tu archivo CSV
    print("Cargando el archivo warehouse.csv...")
    try:
        df = pd.read_csv("warehouse.csv")
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'warehouse.csv'.")
        return

    # 4. Escribir a Delta Lake en el bucket 'retail'
    # Define la ruta destino (puedes cambiar 'warehouse_data' por la carpeta que prefieras)
    delta_path = "s3://retail/raw"
    
    print(f"Escribiendo DataFrame a formato Delta Lake en la ruta: {delta_path}...")
    
    write_deltalake(
        delta_path,
        df,
        storage_options=storage_options,
        mode="overwrite" # Usa "append" si vas a agregar datos sobre una tabla existente
    )
    
    print("¡Ingesta a Delta Lake completada con éxito!")

if __name__ == "__main__":
    ingest_to_delta()