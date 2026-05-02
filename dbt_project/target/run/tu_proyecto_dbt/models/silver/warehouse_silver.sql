
  
    
    

    create  table
      "silver_lake"."main_silver"."warehouse_silver__dbt_tmp"
  
    as (
      

SELECT * FROM "raw_lake"."main"."warehouse"
    );
  
  