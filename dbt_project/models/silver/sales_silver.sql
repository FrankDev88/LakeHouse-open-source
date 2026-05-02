{{ config(
    materialized='table',
    database='my_lake',
    schema='main'
) }}

SELECT 
    * 
FROM {{ source('my_lake', 'warehouse') }} as silver