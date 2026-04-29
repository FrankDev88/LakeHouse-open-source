select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    date as unique_field,
    count(*) as n_records

from "lakehouse"."main"."sales_gold"
where date is not null
group by date
having count(*) > 1



      
    ) dbt_internal_test