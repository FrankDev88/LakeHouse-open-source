-- Este modelo lee desde la capa Bronze (DuckDB local) 
-- y permite usar SQL estándar sin preocuparse por la conexión a Delta Lake/S3



SELECT * 
FROM "lakehouse"."main"."raw_warehouse"