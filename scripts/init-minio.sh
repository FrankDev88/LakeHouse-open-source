#!/bin/sh

# Wait for MinIO to be available using mc
echo "Waiting for MinIO to be available at ${S3_ENDPOINT}..."
until mc alias set local "${S3_ENDPOINT}" "${AWS_ACCESS_KEY_ID}" "${AWS_SECRET_ACCESS_KEY}" > /dev/null 2>&1; do
  echo "MinIO not ready, waiting..."
  sleep 2
done

# Create the lakehouse bucket if it does not exist
if ! mc ls local/lakehouse > /dev/null 2>&1; then
  echo "Creating 'lakehouse' bucket..."
  mc mb local/lakehouse
else
  echo "'lakehouse' bucket already exists."
fi

# Create the retail bucket if it does not exist (needed for silver_warehouse)
if ! mc ls local/retail > /dev/null 2>&1; then
  echo "Creating 'retail' bucket..."
  mc mb local/retail
else
  echo "'retail' bucket already exists."
fi

# Set bucket policy to public (optional, for easier local access)
mc anonymous set public local/lakehouse
mc anonymous set public local/retail

# Create Medallion Architecture folders
# In S3, folders are just object prefixes, but creating an empty object with a trailing slash
# makes them show up as directories in UI/tools.
echo "Creating Medallion Architecture zones..."
mc cp /dev/null local/lakehouse/bronze/ > /dev/null 2>&1 || true
mc cp /dev/null local/lakehouse/silver/ > /dev/null 2>&1 || true
mc cp /dev/null local/lakehouse/gold/ > /dev/null 2>&1 || true

echo "MinIO setup completed successfully!"
