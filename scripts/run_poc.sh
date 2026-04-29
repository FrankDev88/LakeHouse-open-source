#!/bin/bash

# Salir inmediatamente si algún comando falla
set -e

echo -e "\n============================================="
echo "🧪 INICIANDO PRUEBA DE CONCEPTO (PoC) DEL LAKEHOUSE"
echo "============================================="

echo -e "\n[1/3] Verificando salud de la infraestructura..."
MINIO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/minio/health/live)
AIRFLOW_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)

if [ "$MINIO_STATUS" != "200" ] || [ "$AIRFLOW_STATUS" != "200" ]; then
    echo "❌ Error: La infraestructura no está completamente saludable."
    echo "MinIO: $MINIO_STATUS, Airflow: $AIRFLOW_STATUS"
    exit 1
fi
echo "✅ Toda la infraestructura responde correctamente (HTTP 200)."

echo -e "\n[2/3] Ingestando datos crudos a MinIO (Capa Bronze) usando DuckDB..."
docker exec proyecto-1-workspace-1 python -c "
import duckdb, os, boto3
print('-> Asegurando que el bucket existe (S3)...')
s3 = boto3.client('s3', endpoint_url='http://minio:9000', aws_access_key_id='admin', aws_secret_access_key='password123', region_name='us-east-1')
try:
    s3.create_bucket(Bucket='lakehouse')
except Exception as e:
    pass # Ya existe o error menor

print('-> Conectando a DuckDB en memoria...')
conn = duckdb.connect()
conn.execute('INSTALL httpfs; LOAD httpfs; INSTALL aws; LOAD aws;')
conn.execute(\"SET s3_region='us-east-1'; SET s3_endpoint='minio:9000';\")
conn.execute(\"SET s3_access_key_id='admin'; SET s3_secret_access_key='password123';\")
conn.execute(\"SET s3_use_ssl=false; SET s3_url_style='path';\")
conn.execute(\"\"\"
COPY (
    SELECT 1 as id, 'Franko' as customer, 550.00 as amount, '2023-10-01' as date
    UNION ALL
    SELECT 2 as id, 'Arch Linux Corp' as customer, 1200.00 as amount, '2023-10-02' as date
    UNION ALL
    SELECT 3 as id, 'Data Eng' as customer, -50.00 as amount, '2023-10-02' as date
) TO 's3://lakehouse/bronze/sales_raw.parquet' (FORMAT PARQUET);
\"\"\")
print('-> Datos guardados exitosamente en s3://lakehouse/bronze/sales_raw.parquet')
"

echo -e "\n[3/3] Transformando datos con dbt (Capas Silver y Gold en formato Delta)..."
docker exec proyecto-1-workspace-1 bash -c "cd dbt_project && dbt run --profiles-dir . --target dev"
echo "✅ Modelos dbt ejecutados exitosamente."

echo -e "\n🎉 Prueba de Concepto finalizada con éxito."
echo "Puedes consultar tus datos usando scripts/sql_console.sh"
