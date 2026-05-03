from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os

# Paths within the Airflow container
DBT_PROJECT_DIR = "/opt/airflow/dags/dbt_project"
PYTHON_SCRIPTS_DIR = "/opt/airflow/dags/python_scripts"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

with DAG(
    'lakehouse_dbt_pipeline',
    default_args=default_args,
    description='Pipeline orquestado por dbt para el Lakehouse (Medallion Architecture)',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=['dbt', 'lakehouse', 'duckdb'],
) as dag:

    # 1. Ingestar datos a Raw
    ingest_raw = BashOperator(
        task_id='ingest_raw',
        bash_command=f'cd /opt/airflow/dags && python python_scripts/Extract/ingest_raw.py',
    )

    # 2. Inicializar dbt (deps)
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt deps',
    )

    # 3. Ejecutar modelos dbt (Silver -> Gold)
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --profiles-dir .',
        env={
            **os.environ,
            'AWS_REGION': 'us-east-1',
            'AWS_ACCESS_KEY_ID': 'admin',
            'AWS_SECRET_ACCESS_KEY': 'password123',
        }
    )

    # 4. Validar con dbt test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_PROJECT_DIR} && dbt test --profiles-dir .',
    )

    # Definir dependencias
    ingest_raw >> dbt_deps >> dbt_run >> dbt_test
