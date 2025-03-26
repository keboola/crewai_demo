# Runtime API Curl Examples

This document provides practical examples of interacting with the AI Agent Runtime API using curl commands. These examples demonstrate common operations for working with AI agents.

## Prerequisites

- A deployed AI Agent Runtime (using the Management API)
- An API token for authentication
- Access to a terminal with `curl` installed

```bash
# Set your API token as an environment variable
export API_AUTH_TOKEN="your-auth-token-here"

# Set the runtime URL as an environment variable (replace with your runtime URL)
export RUNTIME_URL="https://content-agent.agentic.canary-orion.keboola.dev"
```

## Basic Operations

### 1. Check Runtime Health

Check the health status of the runtime:

```bash
curl "${RUNTIME_URL}/health"
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T12:34:56.789Z",
  "module_loaded": true,
  "active_jobs": 2,
  "version": "0.1.0"
}
```

### 2. List Available Crews

List all available crews that can be used with the kickoff endpoint:

```bash
curl "${RUNTIME_URL}/list-crews" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "crews": [
    {
      "name": "ContentCreationCrew",
      "description": "Crew for generating content",
      "parameters": {
        "brain_dump": {
          "type": "string",
          "description": "The topic to create content about",
          "required": true
        },
        "require_approval": {
          "type": "boolean",
          "description": "Whether to require human approval",
          "required": false,
          "default": false
        }
      }
    },
    {
      "name": "ResearchCrew",
      "description": "Crew for conducting research",
      "parameters": {
        "query": {
          "type": "string",
          "description": "The research query",
          "required": true
        },
        "depth": {
          "type": "integer",
          "description": "Research depth level (1-5)",
          "required": false,
          "default": 3
        }
      }
    }
  ]
}
```

## Job Management

### 3. Start a New Job

Start a new agent job:

```bash
curl -X POST "${RUNTIME_URL}/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Artificial Intelligence",
      "require_approval": true
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

Response:

```json
{
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

### 4. Check Job Status

Check the status of a job:

```bash
# Replace JOB_ID with the ID from the kickoff response
export JOB_ID="987ca65a-62cf-4c48-850b-ad0eb3e37393"

curl "${RUNTIME_URL}/job/${JOB_ID}" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response (Processing):

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Artificial Intelligence"
  },
  "status": "processing",
  "created_at": "2023-06-15T12:34:56.789Z",
  "updated_at": "2023-06-15T12:35:12.345Z",
  "webhook_status_sent": {
    "processing": true,
    "completed": false
  }
}
```

Response (Completed):

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Artificial Intelligence"
  },
  "status": "completed",
  "created_at": "2023-06-15T12:34:56.789Z",
  "completed_at": "2023-06-15T12:40:56.789Z",
  "result": {
    "content": "Artificial Intelligence (AI) refers to...",
    "length": 1234
  },
  "webhook_history": [
    {
      "webhook_id": "whk_20230615123512_a1b2c3d4",
      "status": "processing",
      "sent_at": "2023-06-15T12:35:12.345Z",
      "url": "https://your-webhook-endpoint.com/webhook"
    },
    {
      "webhook_id": "whk_20230615124057_e5f6g7h8",
      "status": "completed",
      "sent_at": "2023-06-15T12:40:57.123Z",
      "url": "https://your-webhook-endpoint.com/webhook"
    }
  ],
  "webhook_status_sent": {
    "processing": true,
    "completed": true
  }
}
```

### 5. List All Jobs

List all jobs with optional filtering:

```bash
# List all jobs (default limit: 10)
curl "${RUNTIME_URL}/jobs" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# List completed jobs with a limit of 5
curl "${RUNTIME_URL}/jobs?status=completed&limit=5" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# Use pagination and sorting
curl "${RUNTIME_URL}/jobs?offset=10&limit=5&sort_by=created_at&sort_order=asc" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "jobs": [
    {
      "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
      "crew": "ContentCreationCrew",
      "status": "completed",
      "created_at": "2023-06-15T12:34:56.789Z",
      "completed_at": "2023-06-15T12:40:56.789Z"
    },
    {
      "id": "123ab45c-78de-9f01-234g-h5i67j8klmno",
      "crew": "ResearchCrew",
      "status": "completed",
      "created_at": "2023-06-15T11:22:33.444Z",
      "completed_at": "2023-06-15T11:30:44.555Z"
    }
  ],
  "count": 2,
  "total_jobs": 15,
  "offset": 0,
  "limit": 5
}
```

### 6. Delete a Job

Delete a job and its associated data:

```bash
curl -X DELETE "${RUNTIME_URL}/job/${JOB_ID}" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "message": "Job deleted successfully",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

## Human-in-the-Loop Workflows

### 7. Start a Job with Approval Requirement

```bash
curl -X POST "${RUNTIME_URL}/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Climate Change",
      "require_approval": true
    }
  }'
```

### 8. Check for Pending Approval

Repeatedly check the job status until it reaches "pending_approval":

```bash
curl "${RUNTIME_URL}/job/${JOB_ID}" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response (Pending Approval):

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Climate Change",
    "require_approval": true
  },
  "status": "pending_approval",
  "created_at": "2023-06-15T12:34:56.789Z",
  "updated_at": "2023-06-15T12:38:32.123Z",
  "partial_result": {
    "content": "Climate Change refers to long-term shifts in temperatures and weather patterns...",
    "awaiting_approval": true,
    "approval_message": "Please review this article draft"
  }
}
```

### 9. Provide Feedback and Approve

Approve the content:

```bash
curl -X POST "${RUNTIME_URL}/job/${JOB_ID}/feedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "feedback": "Content approved as is.",
    "approved": true
  }'
```

Response:

```json
{
  "message": "Feedback recorded and job marked as completed",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

### 10. Request Changes

Provide feedback and request changes:

```bash
curl -X POST "${RUNTIME_URL}/job/${JOB_ID}/feedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "feedback": "Please add more examples about renewable energy.",
    "approved": false
  }'
```

Response:

```json
{
  "message": "Feedback recorded and content generation restarted with feedback",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

## Using Webhooks

### 11. Start a Job with Webhook Notifications

Start a job that will send webhook notifications when status changes:

```bash
curl -X POST "${RUNTIME_URL}/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Artificial Intelligence"
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

For more detailed information about webhook payloads and integration patterns, see the [Webhook Integration Guide](../guides/webhook-integration.md).

## Tips and Best Practices

1. **Use Environment Variables** for base URL and authentication token to make commands more maintainable.
2. **Monitor Job Status** frequently for long-running jobs.
3. **Implement Idempotent Webhooks** to handle duplicate notifications.
4. **Store Job IDs** persistently so you can check their status later.
5. **When Using HITL Workflows**, check job status periodically until it requires approval.

For more information on the Runtime API, see the [Runtime API Documentation](../runtime-api.md).

Last Updated: March 26, 2025 