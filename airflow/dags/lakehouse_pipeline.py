from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Configuración por defecto de las tareas
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def ingest_to_bronze():
    """
    Ingesta de datos crudos (Bronze) directamente a MinIO usando DuckDB.
    Simula la llegada de datos de una fuente externa.
    """
    import duckdb
    import pandas as pd
    
    print("🚀 Iniciando ingesta de datos a la capa Bronze...")
    conn = duckdb.connect()
    
    # Configuración de S3/MinIO
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute("INSTALL aws; LOAD aws;")
    conn.execute(f"SET s3_region='{os.environ.get('AWS_REGION', 'us-east-1')}';")
    conn.execute(f"SET s3_endpoint='{os.environ.get('S3_ENDPOINT', 'minio:9000').replace('http://', '')}';")
    conn.execute(f"SET s3_access_key_id='{os.environ.get('AWS_ACCESS_KEY_ID', 'admin')}';")
    conn.execute(f"SET s3_secret_access_key='{os.environ.get('AWS_SECRET_ACCESS_KEY', 'password123')}';")
    conn.execute("SET s3_use_ssl=false;")
    conn.execute("SET s3_url_style='path';")
    
    # Generación de datos sintéticos más realistas
    data = [
        {'id': 1, 'customer': 'Empresa A', 'amount': 1500.00, 'date': '2023-10-01'},
        {'id': 2, 'customer': 'Empresa B', 'amount': 2300.50, 'date': '2023-10-01'},
        {'id': 3, 'customer': 'Empresa C', 'amount': 850.00, 'date': '2023-10-02'},
        {'id': 4, 'customer': 'Empresa A', 'amount': 1200.00, 'date': '2023-10-02'},
    ]
    df = pd.DataFrame(data)
    
    # Escribir a Bronze (Parquet)
    conn.execute("COPY df TO 's3://lakehouse/bronze/sales_raw.parquet' (FORMAT PARQUET);")
    conn.close()
    print("✅ Ingesta finalizada exitosamente.")

with DAG(
    'lakehouse_medallion_pipeline',
    default_args=default_args,
    description='Pipeline Maestro del Lakehouse: Ingesta Bronze y Transformación dbt (Silver/Gold)',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 10, 1),
    catchup=False,
    tags=['lakehouse', 'medallion', 'dbt', 'duckdb'],
) as dag:

    # 1. Ingesta Inicial a Bronze
    task_ingest_bronze = PythonOperator(
        task_id='ingest_to_bronze',
        python_callable=ingest_to_bronze
    )

    # 2. Transformación con dbt (Silver & Gold)
    # Se utiliza dbt run para materializar las capas analíticas
    task_dbt_run = BashOperator(
        task_id='dbt_run_transformations',
        bash_command='cd /opt/airflow/dags/dbt_project && dbt run'
    )

    # 3. Pruebas de Calidad de Datos
    # Se asegura que los datos procesados cumplan con las reglas de negocio
    task_dbt_test = BashOperator(
        task_id='dbt_test_quality',
        bash_command='cd /opt/airflow/dags/dbt_project && dbt test'
    )

    # Definición del flujo: Ingesta -> Transformación -> Pruebas
    task_ingest_bronze >> task_dbt_run >> task_dbt_test
