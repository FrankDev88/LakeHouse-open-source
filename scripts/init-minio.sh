#!/bin/sh

# Wait for MinIO to be available
echo "Waiting for MinIO to be available at ${S3_ENDPOINT}..."
while ! curl -s "${S3_ENDPOINT}/minio/health/live"; do
  sleep 2
done

# Configure MinIO client (mc)
mc alias set local "${S3_ENDPOINT}" "${AWS_ACCESS_KEY_ID}" "${AWS_SECRET_ACCESS_KEY}"

# Create the lakehouse bucket if it does not exist
if ! mc ls local/lakehouse > /dev/null 2>&1; then
  echo "Creating 'lakehouse' bucket..."
  mc mb local/lakehouse
else
  echo "'lakehouse' bucket already exists."
fi

# Set bucket policy to public (optional, for easier local access)
mc anonymous set public local/lakehouse

# Create Medallion Architecture folders
# In S3, folders are just object prefixes, but creating an empty object with a trailing slash
# makes them show up as directories in UI/tools.
echo "Creating Medallion Architecture zones..."
mc cp /dev/null local/lakehouse/bronze/ > /dev/null 2>&1 || true
mc cp /dev/null local/lakehouse/silver/ > /dev/null 2>&1 || true
mc cp /dev/null local/lakehouse/gold/ > /dev/null 2>&1 || true

echo "MinIO setup completed successfully!"
