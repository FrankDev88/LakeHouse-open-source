{{ config(
    materialized='table',
    database='silver_lake',
    alias='warehouse_silver'
) }}

SELECT * FROM {{ source('raw_lake', 'warehouse') }}