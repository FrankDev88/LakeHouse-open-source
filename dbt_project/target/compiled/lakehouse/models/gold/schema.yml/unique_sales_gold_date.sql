
    
    

select
    date as unique_field,
    count(*) as n_records

from "lakehouse"."main"."sales_gold"
where date is not null
group by date
having count(*) > 1


