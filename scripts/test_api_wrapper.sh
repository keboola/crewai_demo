#!/bin/bash

# Set environment variables
export DATA_APP_ENTRYPOINT="$1"

if [ -z "$DATA_APP_ENTRYPOINT" ]; then
    echo "Usage: $0 <path_to_entrypoint>"
    echo "Example: $0 convo_newsletter_crew/src/convo_newsletter_crew/main.py"
    exit 1
fi

echo "Using entrypoint: $DATA_APP_ENTRYPOINT"

# Start the API server
echo "Starting API server..."
uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8000 --reload 