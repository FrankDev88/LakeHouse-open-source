import duckdb

con = duckdb.connect()
con.execute("LOAD httpfs; LOAD ducklake;")
con.execute("""
    CREATE SECRET IF NOT EXISTS minio_secret (
        TYPE S3, KEY_ID 'admin', SECRET 'password123',
        REGION 'us-east-1', ENDPOINT 'minio:9000',
        URL_STYLE 'path', USE_SSL false
    );
""")

# Attach las 3 capas
for alias, path in [
    ("raw_lake",    "s3://retail/raw/"),
    ("silver_lake", "s3://retail/silver/"),
    ("gold_lake",   "s3://retail/gold/"),
]:
    try:
        con.execute(f"""
            ATTACH 'ducklake:/workspace/dbt_project/{alias.replace('_lake','')}_metadata.ducklake' 
            AS {alias} (DATA_PATH '{path}');
        """)
        print(f"✅ {alias} conectado")
    except Exception as e:
        print(f"⚠️  {alias}: {e}")

print("\n📦 Tablas disponibles:")
print(con.execute("SHOW ALL TABLES;").df()[['database','schema','name']].to_string(index=False))

print("\n💬 Escribe tus queries SQL (o 'exit' para salir)")
print("   Ejemplo: SELECT * FROM raw_lake.warehouse LIMIT 5;")
print("-" * 60)

while True:
    try:
        query = input("\nSQL> ").strip()
        if query.lower() in ('exit', 'quit', 'q'):
            break
        if not query:
            continue
        result = con.execute(query).df()
        print(result.to_string(index=False))
        print(f"\n({len(result)} filas)")
    except Exception as e:
        print(f"❌ Error: {e}")

con.close()