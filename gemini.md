# 🧠 Entorno de Desarrollo y Arquitectura Técnica

## 💻 Información del Entorno
- **OS:** Arch Linux (Rolling Release)
- **WM/Compositor:** Hyprland
- **Runtime:** Docker Engine v24+
- **Workspace:** `/home/franko/DataEnginer/proyecto-1`

---

## 🏗️ Arquitectura: Local Data Lakehouse (Zero-Spark)

Este proyecto implementa un Lakehouse funcional sin la sobrecarga de Spark, utilizando la arquitectura **DuckLake** que combina **DuckDB** con la extensión **ducklake** para la gestión unificada de metadatos y almacenamiento.

### 🧩 Componentes Críticos

#### 1. DuckDB + DuckLake (The Engine & Storage Layer)
- **Extensión DuckLake:** DuckDB utiliza la extensión `ducklake` para gestionar tanto el catálogo de metadatos como la persistencia física de las tablas.
- **Catálogos Desacoplados:** Usamos archivos `.ducklake` para separar `raw`, `silver` y `gold`. Cada uno mapea un prefijo de S3 en MinIO.
- **Configuración de Secretos:** Los secretos de S3 se gestionan a nivel de sesión para facilitar el acceso a MinIO.
- **Interoperabilidad:** DuckLake abstrae la complejidad de los formatos de archivos subyacentes, permitiendo tratar las rutas de S3 como tablas relacionales nativas.

#### 2. dbt-duckdb (The Orchestrator)
- **Integración con DuckLake:** dbt utiliza el archivo `dbt_metadata.duckdb` como motor principal, pero se conecta a los catálogos de DuckLake mediante el comando `ATTACH`.
- **Modelos Híbridos:** 
  - **SQL:** Usado para la mayoría de las transformaciones. dbt aprovecha la integración nativa con DuckLake.
- **Profiles:** Configurado para inyectar variables de entorno (`AWS_ACCESS_KEY_ID`, `S3_ENDPOINT`).

#### 3. DuckLake Storage (The Single Source of Truth)
- **Protocolo:** Gestión directa sobre MinIO mediante la extensión DuckLake.
- **Independencia:** Si los archivos de metadatos locales se pierden, la estructura de datos en MinIO permite la reconexión y reconstrucción del catálogo mediante DuckLake.
- **Escritura:** dbt materializa las tablas directamente en los catálogos "attached" de DuckLake.
- **Consumo:** Se accede mediante SQL estándar apuntando al alias del catálogo (ej. `SELECT * FROM silver_lake.schema.table`).

---

## 🛠️ Guía de Desarrollo para la IA

Cuando trabajes en este proyecto, sigue estos patrones:

1.  **Pensamiento DuckLake:** Los datos están en el Lago (MinIO) y los metadatos están gestionados por catálogos DuckLake. No asumas que todo vive en un solo archivo de base de datos.
2.  **Materialización DuckLake:** Usa modelos SQL estándar en dbt. DuckLake se encarga de persistir los datos en S3 automáticamente basándose en la configuración de `attach` en `profiles.yml`.
3.  **Conectividad S3:** Asegúrate de que `on-run-start` en dbt cargue las extensiones `httpfs` y `ducklake` y configure el secreto S3.
4.  **Uso de ATTACH:** Para acceder a los datos, usa el esquema `[alias_lake].[schema].[table]` según lo definido en `profiles.yml`.
5.  **Medallion Logic:**
    - **Bronze:** `s3://lakehouse/bronze/*.parquet`
    - **Silver:** `s3://lakehouse/silver/[table_name]`
    - **Gold:** `s3://lakehouse/gold/[table_name]`

