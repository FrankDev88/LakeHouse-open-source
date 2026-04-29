#!/bin/bash

echo -e "\n============================================="
echo "🦆 ABRIENDO CONSOLA SQL DEL LAKEHOUSE (DUCKDB)"
echo "============================================="
echo "Las credenciales de S3 (MinIO) y las extensiones se cargarán automáticamente."
echo "Puedes consultar tus datos usando la función nativa de Delta Lake, por ejemplo:"
echo -e "\n  SELECT * FROM delta_scan('s3://lakehouse/gold/sales_gold');"
echo -e "  SELECT * FROM delta_scan('s3://lakehouse/silver/sales_silver');"
echo -e "\nPara salir de la consola escribe: .exit"
echo "---------------------------------------------"

docker exec -it proyecto-1-workspace-1 bash -c "
if [ ! -f /workspace/duckdb ]; then
    echo 'Instalando DuckDB CLI interactivo en el workspace (solo tomará unos segundos)...'
    apt-get update -qq && apt-get install -y -qq wget unzip > /dev/null
    wget -qO duckdb.zip https://github.com/duckdb/duckdb/releases/latest/download/duckdb_cli-linux-amd64.zip
    unzip -q duckdb.zip
    rm duckdb.zip
    chmod +x duckdb
fi

# Iniciar la consola leyendo el archivo de inicialización y la base de datos persistente
/workspace/duckdb /workspace/lakehouse.duckdb -init /workspace/scripts/.duckdb_init.sql
"
