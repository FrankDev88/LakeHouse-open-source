# 🧠 Entorno de Desarrollo y Arquitectura Técnica

## 💻 Información del Entorno
- **OS:** Arch Linux (Rolling Release)
- **WM/Compositor:** Hyprland
- **Runtime:** Docker Engine v24+
- **Workspace:** `/home/franko/DataEnginer/proyecto-1`

---

## 🏗️ Arquitectura: Local Data Lakehouse (Zero-Spark)

Este proyecto implementa un Lakehouse funcional sin la sobrecarga de Spark, utilizando **DuckDB** como motor de ejecución y **Delta Lake** como capa de almacenamiento transaccional.

### 🧩 Componentes Críticos

#### 1. DuckDB (The Engine & Catalog)
- **Rol Dual:** Actúa como motor de ejecución (Compute) y como **Metastore/Catálogo** local (archivo `.duckdb`).
- **Persistencia de Metadatos:** El archivo `.duckdb` NO almacena filas de datos de negocio; almacena definiciones de vistas, esquemas de tablas externas y punteros hacia MinIO.
- **Configuración de Secretos:** Para acceder a MinIO, usamos `CREATE SECRET` con el tipo `S3`. Esto se guarda en el catálogo para persistencia entre sesiones.
- **Interoperabilidad:** Capacidad de leer Parquet nativo de la capa Bronze y escanear tablas Delta de las capas Silver/Gold.

#### 2. dbt-duckdb (The Orchestrator)
- **Gestión de Grafo:** dbt utiliza el archivo `.duckdb` para registrar cada modelo exitoso.
- **Modelos Híbridos:** 
  - **SQL:** Usado para transformaciones sencillas y vistas. dbt guarda el SQL compilado en el catálogo.
  - **Python:** Crucial para la escritura en Delta Lake usando la librería `deltalake`.
- **Profiles:** Configurado para inyectar variables de entorno (`AWS_ACCESS_KEY_ID`, `S3_ENDPOINT`).

#### 3. Delta Lake (The Storage - Single Source of Truth)
- **Protocolo:** Implementación "Path-Based" sobre MinIO.
- **Independencia:** Si el archivo `.duckdb` se corrompe, los datos en formato Delta permiten la reconstrucción total del estado del Lakehouse.
- **Escritura:** Se realiza mediante `write_deltalake` en modelos de Python.
- **Consumo:** DuckDB lee mediante la función `delta_scan('s3://...')`.

---

## 🛠️ Guía de Desarrollo para la IA

Cuando trabajes en este proyecto, sigue estos patrones:

1.  **Pensamiento Lakehouse:** Recuerda que los datos NO están en la base de datos local, están en el Lago (MinIO). El archivo `.duckdb` es solo tu "Unity Catalog" local.
2.  **Materialización Delta:** Si el usuario pide crear una tabla en la capa Silver o Gold, prefiere un **modelo de Python** (.py) que use `deltalake.write_deltalake`.
3.  **Conectividad S3:** Siempre verifica que las `storage_options` incluyan `"AWS_ALLOW_HTTP": "true"` y `"AWS_S3_ALLOW_UNSAFE_RENAME": "true"`.
4.  **Secrets:** Siempre inicializa o verifica la existencia de `minio_s3` antes de consultas manuales fuera de dbt.
5.  **Medallion Logic:**
    - **Bronze:** `s3://lakehouse/bronze/*.parquet`
    - **Silver:** `s3://lakehouse/silver/[table_name]`
    - **Gold:** `s3://lakehouse/gold/[table_name]`

