

SELECT
    id,
    customer,
    amount,
    date,
    CURRENT_TIMESTAMP AS _processed_at
FROM read_parquet('s3://lakehouse/bronze/sales_raw.parquet')
WHERE amount > 0