#!/bin/bash
# Start Jupyter Lab in the workspace container
# Usage: docker compose exec workspace bash /workspace/scripts/start-jupyter.sh

echo "🚀 Starting Jupyter Lab..."
jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --notebook-dir=/workspace \
    --ServerApp.token='' \
    --ServerApp.password='' \
    --ServerApp.allow_origin='*'

