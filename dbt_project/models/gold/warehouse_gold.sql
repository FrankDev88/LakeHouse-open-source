{{ config(
    materialized='table',
    database='gold_lake',
    alias='warehouse_gold'
) }}

SELECT
*
FROM {{ ref('warehouse_silver') }}