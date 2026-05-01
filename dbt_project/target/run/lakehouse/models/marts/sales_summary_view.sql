
  
    
    

    create  table
      "lakehouse"."main"."sales_summary_view__dbt_tmp"
  
    as (
      

SELECT
    date,
    total_sales,
    total_transactions,
    (total_sales / total_transactions) as ticket_promedio,
    _processed_at
FROM "lakehouse"."main"."sales_gold"
ORDER BY date DESC
    );
  
  