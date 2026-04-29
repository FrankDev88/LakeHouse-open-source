create or replace view "lakehouse"."main"."sales_gold__dbt_int" as (
        select * from 's3://lakehouse/gold/sales_gold.parquet'
    );