
  
    
    

    create  table
      "my_lake"."main_main"."sales_silver__dbt_tmp"
  
    as (
      

SELECT 
    * 
FROM "my_lake"."main"."warehouse" as silver
    );
  
  