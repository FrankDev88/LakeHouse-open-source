SELECT *
FROM {{ source('pos_landing', 'raw_sales') }}
