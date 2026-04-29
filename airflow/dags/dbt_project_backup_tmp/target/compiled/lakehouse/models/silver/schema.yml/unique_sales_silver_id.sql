
    
    

select
    id as unique_field,
    count(*) as n_records

from "lakehouse"."main"."sales_silver"
where id is not null
group by id
having count(*) > 1


