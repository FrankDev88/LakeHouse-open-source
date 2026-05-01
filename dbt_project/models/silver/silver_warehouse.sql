{{ config(
    materialized='external',
    location='s3://retail/silver/warehouse',
    format='delta' 
) }}

SELECT * 
FROM {{ source('retail', 'raw') }}