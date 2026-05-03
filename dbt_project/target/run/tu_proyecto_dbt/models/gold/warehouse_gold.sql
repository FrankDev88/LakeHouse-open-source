
  
    
    

    create  table
      "gold_lake"."main_gold"."warehouse_gold__dbt_tmp"
  
    as (
      

SELECT
*
FROM "silver_lake"."main_silver"."warehouse_silver"
    );
  
  