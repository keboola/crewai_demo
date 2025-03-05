#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    set -a
    source .env
    set +a
else
    echo "Warning: .env file not found"
fi

# Set environment variables - this will override any values from .env
export DATA_APP_ENTRYPOINT="convo_newsletter_crew/src/convo_newsletter_crew/main.py"
echo "Overriding DATA_APP_ENTRYPOINT to: $DATA_APP_ENTRYPOINT"

# Check if required environment variables are set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set."
    echo "Please set it before running this script:"
    echo "export ANTHROPIC_API_KEY=your_anthropic_api_key"
    exit 1
fi

if [ -z "$EXA_API_KEY" ]; then
    echo "Warning: EXA_API_KEY environment variable is not set."
    echo "Some functionality may not work properly."
    echo "Please set it before running this script:"
    echo "export EXA_API_KEY=your_exa_api_key"
fi

# MODEL is optional, but we'll check for it
if [ -z "$MODEL" ]; then
    echo "Info: MODEL environment variable is not set."
    echo "Will use the default model: anthropic/claude-3-sonnet-20240229-v1:0"
    echo "To use a different model, set the MODEL environment variable:"
    echo "export MODEL=your_preferred_model"
fi

echo "Using entrypoint: $DATA_APP_ENTRYPOINT"
echo "ANTHROPIC_API_KEY is set"
if [ -n "$EXA_API_KEY" ]; then
    echo "EXA_API_KEY is set"
fi
if [ -n "$MODEL" ]; then
    echo "MODEL is set to: $MODEL"
fi

# Start the API server
echo "Starting API server..."
source .venv/bin/activate && uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8000 --reload 