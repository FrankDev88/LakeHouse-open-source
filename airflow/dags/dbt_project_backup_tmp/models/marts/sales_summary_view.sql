{{ config(materialized='table') }}

SELECT
    date,
    total_sales,
    total_transactions,
    (total_sales / total_transactions) as ticket_promedio,
    _processed_at
FROM {{ ref('sales_gold') }}
ORDER BY date DESC
