# Archivo: /workspace/dbt_project/init_lake.py
import duckdb

# Conectamos al archivo que usa tu profiles.yml
con = duckdb.connect('local_dbt.duckdb')

# 1. Cargamos extensiones necesarias
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL ducklake; LOAD ducklake;")

# 2. Creamos el secreto de forma PERSISTENTE
# Al ser PERSISTENT, se guarda en el archivo .duckdb y dbt lo verá
con.execute("""
CREATE PERSISTENT SECRET IF NOT EXISTS minio_secret (
    TYPE S3, 
    KEY_ID 'admin', 
    SECRET 'password123', 
    REGION 'us-east-1', 
    ENDPOINT 'minio:9000', 
    URL_STYLE 'path', 
    USE_SSL false
);
""")

# 3. Atachamos el catálogo forzando la ruta
# Usamos el OVERRIDE para que no te vuelva a dar la "Nota"
try:
    con.execute("""
        ATTACH 'ducklake:/workspace/retail_metadata.ducklake' AS my_lake 
        (DATA_PATH 's3://retail/', OVERRIDE_DATA_PATH true);
    """)
    print("✅ Catálogo 'my_lake' anclado correctamente.")
except Exception as e:
    print(f"Error al atachar: {e}")

# 4. TRUCO FINAL: Crear un objeto vacío para forzar a DuckDB a guardar el estado
con.execute("CREATE TABLE IF NOT EXISTS dbt_init_check AS SELECT 1;")

con.close()
print("🚀 Base de datos 'local_dbt.duckdb' lista para dbt.")