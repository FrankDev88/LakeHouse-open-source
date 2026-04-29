INSTALL httpfs; LOAD httpfs;
INSTALL aws; LOAD aws;
INSTALL delta; LOAD delta;
CREATE SECRET IF NOT EXISTS minio_s3 (
    TYPE S3,
    KEY_ID 'admin',
    SECRET 'password123',
    REGION 'us-east-1',
    ENDPOINT 'minio:9000',
    URL_STYLE 'path',
    USE_SSL false
);

.prompt 'lakehouse-sql> '
