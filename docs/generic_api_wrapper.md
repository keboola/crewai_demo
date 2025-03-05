# Generic API Wrapper Documentation

This document provides detailed information about the generic API wrapper for CrewAI implementations.

## Overview

The generic API wrapper is designed to work with any CrewAI implementation, regardless of how it's structured. It provides a RESTful API for interacting with CrewAI crews, allowing you to kickoff jobs, check job status, and more.

## Key Features

- **Flexible Path Handling**: Automatically adds necessary directories to the Python path to handle various project structures.
- **Dynamic Crew Initialization**: Tries different initialization patterns to accommodate various crew implementations.
- **Adaptive Kickoff Method**: Supports both crews that accept inputs in the kickoff method and those that don't.
- **CrewBase Support**: Works with crews implemented using the CrewBase decorator pattern.
- **Environment Variable Support**: Loads environment variables from `.env` files and allows setting them via the API.
- **Asynchronous Job Processing**: Jobs are processed in the background, allowing the API to respond quickly.
- **Job Status Tracking**: Track the status of jobs and retrieve results when they're complete.
- **Webhook Support**: Receive notifications when jobs are complete or require approval.

## Environment Variable Support

The API wrapper supports multiple ways to provide environment variables to your CrewAI implementation:

1. **OS Environment Variables**: Set variables in your shell before starting the API server
2. **`.env` File**: Place a `.env` file in the project root with your environment variables
3. **`.streamlit/secrets.toml`**: Use Streamlit's secrets management for environment variables
4. **API Request**: Pass environment variables in the request body when calling the `/kickoff` endpoint

The API wrapper automatically loads variables from `.env` and `.streamlit/secrets.toml` files at startup, making it easy to configure your application without modifying code.

### Priority Order

Environment variables are loaded in the following order, with later sources overriding earlier ones:

1. Variables from `.env` file
2. Variables from `.streamlit/secrets.toml`
3. Variables from the OS environment
4. Variables from the API request body

This allows you to set default values in configuration files while still being able to override them when needed.

## API Endpoints

### Kickoff a Crew

```
POST /kickoff
```

Start a new job with a specified crew.

**Request Body:**

```json
{
  "crew": "YourCrewName",
  "inputs": {
    "key1": "value1",
    "key2": "value2"
  },
  "env_vars": {
    "API_KEY": "your-api-key",
    "MODEL": "your-model-name"
  },
  "webhook_url": "https://your-webhook-url.com",
  "wait": false
}
```

**Parameters:**

- `crew` (string, required): The name of the crew to use.
- `inputs` (object, optional): Input data for the crew.
- `env_vars` (object, optional): Environment variables to set for this job.
- `webhook_url` (string, optional): URL to send job status updates to.
- `wait` (boolean, optional): Whether to wait for the job to complete before responding. Default is `false`.

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

### Get Job Status

```
GET /job/{job_id}
```

Get the status of a job.

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "crew": "YourCrewName",
  "status": "completed",
  "created_at": "2023-01-01T00:00:00.000Z",
  "completed_at": "2023-01-01T00:01:00.000Z",
  "result": {
    "content": "Job result content",
    "length": 18
  }
}
```

### Provide Feedback

```
POST /job/{job_id}/feedback
```

Provide feedback for a job that requires approval.

**Request Body:**

```json
{
  "approved": true,
  "feedback": "Looks good!"
}
```

**Parameters:**

- `approved` (boolean, required): Whether to approve the job.
- `feedback` (string, optional): Feedback to provide.

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "message": "Feedback received and job is being processed"
}
```

### List Jobs

```
GET /jobs
```

List all jobs.

**Query Parameters:**

- `limit` (integer, optional): Maximum number of jobs to return. Default is 10.
- `status` (string, optional): Filter jobs by status.

**Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "crew": "YourCrewName",
    "status": "completed",
    "created_at": "2023-01-01T00:00:00.000Z",
    "completed_at": "2023-01-01T00:01:00.000Z"
  }
]
```

### List Crews

```
GET /list-crews
```

List all available crews.

**Response:**

```json
[
  "YourCrewName",
  "AnotherCrewName"
]
```

### Delete Job

```
DELETE /job/{job_id}
```

Delete a job.

**Response:**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "deleted",
  "message": "Job deleted successfully"
}
```

## Usage Examples

### Starting the API Server

```bash
# Set the entrypoint to your main script
export DATA_APP_ENTRYPOINT="path/to/your/main.py"

# Make sure required environment variables are set
export ANTHROPIC_API_KEY="your_anthropic_api_key"  # For ConvoNewsletterCrew
export OPENAI_API_KEY="your_openai_api_key"        # For other crews

# Start the API server
uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8000
```

Or use the provided script:

```bash
./scripts/test_api_wrapper.sh path/to/your/main.py
```

### Testing with Curl

```bash
# Kickoff a job
curl -X POST http://localhost:8000/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "YourCrewName",
    "inputs": {
      "your_input_key": "your_input_value"
    },
    "env_vars": {
      "ANTHROPIC_API_KEY": "your_anthropic_api_key"
    }
  }'

# Check job status
curl -X GET http://localhost:8000/job/{job_id}

# Provide feedback
curl -X POST http://localhost:8000/job/{job_id}/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "feedback": "Looks good!"
  }'

# List all jobs
curl -X GET http://localhost:8000/jobs

# List available crews
curl -X GET http://localhost:8000/list-crews

# Delete a job
curl -X DELETE http://localhost:8000/job/{job_id}
```

## Troubleshooting

### Common Issues

1. **Module Not Found Error**: Make sure the `DATA_APP_ENTRYPOINT` environment variable is set correctly and points to your main script.

2. **Crew Not Found Error**: Make sure the crew name you're using exists in your main script.

3. **Initialization Error**: If you're getting an error during crew initialization, make sure your crew class can be initialized either with or without inputs.

4. **Kickoff Error**: If you're getting an error during kickoff, make sure your crew's kickoff method can accept inputs if needed.

5. **Missing Environment Variables**: If you're getting an error about missing environment variables (e.g., `ANTHROPIC_API_KEY not found`), make sure to set them in your `.env` file or provide them in the `env_vars` field of the kickoff request.

### Debugging

The API wrapper logs detailed information about what it's doing. Check the logs for more information about errors.

## Advanced Configuration

### Environment Variables

- `DATA_APP_ENTRYPOINT`: Path to your main script.
- `LOG_LEVEL`: Logging level (default: INFO).
- `ANTHROPIC_API_KEY`: Required for crews using Anthropic's Claude model.
- `OPENAI_API_KEY`: Required for crews using OpenAI models.
- `AZURE_OPENAI_API_KEY`: Required for crews using Azure OpenAI.

### Webhook Notifications

You can provide a webhook URL when kickoff a job to receive notifications when the job status changes. The webhook will receive a POST request with the following body:

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "crew": "YourCrewName",
  "result": {
    "content": "Job result content",
    "length": 18
  }
}
``` 