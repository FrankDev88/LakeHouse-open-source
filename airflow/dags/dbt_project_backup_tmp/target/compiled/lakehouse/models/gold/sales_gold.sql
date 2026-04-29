

SELECT
    date,
    COUNT(id) as total_transactions,
    SUM(amount) as total_sales,
    CURRENT_TIMESTAMP as _processed_at
FROM "lakehouse"."main"."sales_silver"
GROUP BY date