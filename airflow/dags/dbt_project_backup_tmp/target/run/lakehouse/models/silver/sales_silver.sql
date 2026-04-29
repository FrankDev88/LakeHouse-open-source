create or replace view "lakehouse"."main"."sales_silver__dbt_int" as (
        select * from 's3://lakehouse/silver/sales_silver.parquet'
    );