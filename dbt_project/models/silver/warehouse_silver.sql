{{ config(
    materialized='table',
    database='silver_lake'
) }}

SELECT * FROM {{ source('raw_lake', 'warehouse') }}