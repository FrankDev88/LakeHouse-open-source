-- Este modelo lee desde la capa Bronze (DuckDB local) 
-- y permite usar SQL estándar sin preocuparse por la conexión a Delta Lake/S3

{{ config(
    materialized='table'
) }}

SELECT * 
FROM {{ ref('raw_warehouse') }}
