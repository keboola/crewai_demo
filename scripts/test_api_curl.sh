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

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment"
    source .venv/bin/activate
else
    echo "Warning: Virtual environment not found at .venv"
    echo "Python commands may fail if Python is not in your PATH"
fi

# Set the API base URL
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the crew name from command line argument
CREW_NAME="$1"

if [ -z "$CREW_NAME" ]; then
    echo -e "${RED}Usage: $0 <crew_name>${NC}"
    echo -e "${YELLOW}Example: $0 ConvoNewsletterCrew${NC}"
    exit 1
fi

echo -e "${BLUE}Testing API with crew: $CREW_NAME${NC}"

# Step 1: List available crews
echo -e "${YELLOW}Step 1: Listing available crews${NC}"
echo "curl -X GET $API_URL/list-crews"

CREWS_RESPONSE=$(curl -s -X GET $API_URL/list-crews)

echo -e "${GREEN}Response:${NC}"
echo $CREWS_RESPONSE | python -m json.tool
echo ""

# Prepare environment variables for the request
ENV_VARS=""
if [ "$CREW_NAME" = "ConvoNewsletterCrew" ]; then
    # Start with an empty JSON object
    ENV_VARS=', "env_vars": {'
    
    # Add ANTHROPIC_API_KEY if set
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        ENV_VARS="$ENV_VARS\"ANTHROPIC_API_KEY\": \"$ANTHROPIC_API_KEY\""
        echo -e "${GREEN}Including ANTHROPIC_API_KEY in request${NC}"
    else
        echo -e "${RED}Error: ANTHROPIC_API_KEY not set. ConvoNewsletterCrew will fail.${NC}"
        exit 1
    fi
    
    # Add EXA_API_KEY if set
    if [ -n "$EXA_API_KEY" ]; then
        # Add a comma if we already have ANTHROPIC_API_KEY
        if [ -n "$ANTHROPIC_API_KEY" ]; then
            ENV_VARS="$ENV_VARS, "
        fi
        ENV_VARS="$ENV_VARS\"EXA_API_KEY\": \"$EXA_API_KEY\""
        echo -e "${GREEN}Including EXA_API_KEY in request${NC}"
    else
        echo -e "${YELLOW}Warning: EXA_API_KEY not set. Some functionality may not work.${NC}"
    fi
    
    # Add MODEL if set
    if [ -n "$MODEL" ]; then
        # Add a comma if we already have other variables
        if [ -n "$ANTHROPIC_API_KEY" ] || [ -n "$EXA_API_KEY" ]; then
            ENV_VARS="$ENV_VARS, "
        fi
        ENV_VARS="$ENV_VARS\"MODEL\": \"$MODEL\""
        echo -e "${GREEN}Including MODEL in request: $MODEL${NC}"
    fi
    
    # Close the JSON object
    ENV_VARS="$ENV_VARS}"
fi

# Step 2: Kickoff a job
echo -e "${YELLOW}Step 2: Kickoff a job with $CREW_NAME${NC}"
KICKOFF_DATA='{
    "crew": "'$CREW_NAME'",
    "inputs": {
      "brain_dump": "Test brain dump for API testing"
    }'$ENV_VARS'
  }'

echo "curl -X POST $API_URL/kickoff -H \"Content-Type: application/json\" -d '$KICKOFF_DATA'"

RESPONSE=$(curl -s -X POST $API_URL/kickoff \
  -H "Content-Type: application/json" \
  -d "$KICKOFF_DATA")

echo -e "${GREEN}Response:${NC}"
echo $RESPONSE | python -m json.tool

# Extract job_id from response
JOB_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))")

if [ -z "$JOB_ID" ]; then
  echo -e "${RED}Failed to get job_id from response. Exiting.${NC}"
  exit 1
fi

echo -e "${GREEN}Job ID: $JOB_ID${NC}"
echo ""

# Step 3: Check job status
echo -e "${YELLOW}Step 3: Checking job status${NC}"
echo "curl -X GET $API_URL/job/$JOB_ID"

JOB_RESPONSE=$(curl -s -X GET $API_URL/job/$JOB_ID)
echo -e "${GREEN}Job Status:${NC}"
echo $JOB_RESPONSE | python -m json.tool
echo ""

# Step 4: List all jobs
echo -e "${YELLOW}Step 4: Listing all jobs${NC}"
echo "curl -X GET $API_URL/jobs"

JOBS_RESPONSE=$(curl -s -X GET $API_URL/jobs)
echo -e "${GREEN}All Jobs:${NC}"
echo $JOBS_RESPONSE | python -m json.tool
echo ""

echo -e "${BLUE}API testing completed!${NC}" 