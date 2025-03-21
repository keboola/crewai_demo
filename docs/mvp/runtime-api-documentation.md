# AI Agent Runtime API

> [!NOTE]
> This documentation explains how to use the AI Agent Runtime API to interact with your deployed CrewAI agents on the AI Agent Platform.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Kickoff Endpoint](#kickoff-endpoint)
  - [Job Status](#job-status)
  - [Feedback Endpoint](#feedback-endpoint)
  - [List Jobs](#list-jobs)
  - [List Crews](#list-crews)
  - [Delete Job](#delete-job)
- [Webhook Notifications](#webhook-notifications)
- [Job States](#job-states)
- [Human-in-the-Loop Workflows](#human-in-the-loop-workflows)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

The AI Agent Runtime API provides a RESTful interface for interacting with your deployed CrewAI agents. Each AI Agent Runtime deployed through the Management API has its own API endpoint that enables:

- **Asynchronous execution** of CrewAI workflows
- **Human-in-the-Loop (HITL)** approval processes
- **Webhook notifications** for job status updates
- **Job tracking** across multiple executions
- **Crew discovery** to explore available agent crews

## Quick Start

Once you've deployed an AI Agent Runtime using the Management API, you can interact with it through its API:

1. **Find your runtime URL**:
   ```bash
   # If your runtime is named "content-agent"
   https://content-agent.agentic.canary-orion.keboola.dev
   ```

2. **Run your first job**:
   ```bash
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Artificial Intelligence"
       }
     }'
   ```

3. **Check job status** (using the job_id from the response):
   ```bash
   curl "https://content-agent.agentic.canary-orion.keboola.dev/job/987ca65a-62cf-4c48-850b-ad0eb3e37393"
   ```

## API Endpoints

### Health Check

**Endpoint**: `GET /health`

Returns the health status of the AI Agent Runtime.

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/health"
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T12:34:56.789Z",
  "module_loaded": true,
  "active_jobs": 2,
  "version": "0.1.0"
}
```

### Kickoff Endpoint

**Endpoint**: `POST /kickoff`

Starts a new agent job.

**Request Body**:

```json
{
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Artificial Intelligence",
    "require_approval": true
  },
  "webhook_url": "https://your-webhook-endpoint.com/webhook"
}
```

**Parameters**:
- `crew` (string, required): The name of the crew class to use
- `inputs` (object): Input parameters for the crew
- `webhook_url` (string, optional): URL to receive job status updates

**Example**:

```bash
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Artificial Intelligence",
      "require_approval": true
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

**Response**:

```json
{
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

### Job Status

**Endpoint**: `GET /job/{job_id}`

Retrieves the status and result of a specific job.

**Path Parameters**:
- `job_id`: ID of the job to retrieve

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/job/987ca65a-62cf-4c48-850b-ad0eb3e37393"
```

**Response (Processing)**:

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Artificial Intelligence"
  },
  "status": "processing",
  "created_at": "2023-06-15T12:34:56.789Z",
  "updated_at": "2023-06-15T12:35:12.345Z"
}
```

**Response (Completed)**:

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
  }
}
```

**Response (Pending Approval)**:

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "brain_dump": "Artificial Intelligence",
    "require_approval": true
  },
  "status": "pending_approval",
  "created_at": "2023-06-15T12:34:56.789Z",
  "updated_at": "2023-06-15T12:38:32.123Z",
  "partial_result": {
    "content": "Artificial Intelligence (AI) refers to...",
    "awaiting_approval": true,
    "approval_message": "Please review this article draft"
  }
}
```

### Feedback Endpoint

**Endpoint**: `POST /job/{job_id}/feedback`

Provides human feedback for a job that's pending approval.

**Path Parameters**:
- `job_id`: ID of the job to provide feedback for

**Request Body**:
```json
{
  "feedback": "Please make the content more concise and add more examples.",
  "approved": false
}
```

**Parameters**:
- `feedback` (string): Human feedback on the content
- `approved` (boolean): Whether to approve the content as is

**Example**:

```bash
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/job/987ca65a-62cf-4c48-850b-ad0eb3e37393/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please make the content more concise and add more examples.",
    "approved": false
  }'
```

**Response (Approved)**:

```json
{
  "message": "Feedback recorded and job marked as completed",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

**Response (Not Approved)**:

```json
{
  "message": "Feedback recorded and content generation restarted with feedback",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

### List Jobs

**Endpoint**: `GET /jobs`

Lists all jobs with optional filtering.

**Query Parameters**:
- `limit` (integer, optional): Maximum number of jobs to return (default: 10)
- `status` (string, optional): Filter jobs by status
- `offset` (integer, optional): Pagination offset for large result sets (default: 0)
- `sort_by` (string, optional): Field to sort by (default: "created_at")
- `sort_order` (string, optional): Sort direction, "asc" or "desc" (default: "desc")

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/jobs?limit=5&status=completed"
```

**Response**:

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

### List Crews

**Endpoint**: `GET /list-crews`

Lists all available crews that can be used with the kickoff endpoint.

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/list-crews"
```

**Response**:

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

### Delete Job

**Endpoint**: `DELETE /job/{job_id}`

Deletes a job and its associated data.

**Path Parameters**:
- `job_id`: ID of the job to delete

**Example**:

```bash
curl -X DELETE "https://content-agent.agentic.canary-orion.keboola.dev/job/987ca65a-62cf-4c48-850b-ad0eb3e37393"
```

**Response**:

```json
{
  "message": "Job deleted successfully",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

## Webhook Notifications

The API can send webhook notifications to a URL you specify when a job's status changes. This is useful for implementing asynchronous workflows.

To use webhooks, include a `webhook_url` parameter when starting a job:

```bash
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Artificial Intelligence"
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

### Webhook Payload Examples

**Job Created**:
```json
{
  "event": "job_created",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "queued",
  "crew": "ContentCreationCrew",
  "created_at": "2023-06-15T12:34:56.789Z"
}
```

**Job Completed**:
```json
{
  "event": "job_completed",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "completed",
  "crew": "ContentCreationCrew",
  "created_at": "2023-06-15T12:34:56.789Z",
  "completed_at": "2023-06-15T12:40:56.789Z",
  "result": {
    "content": "Artificial Intelligence (AI) refers to...",
    "length": 1234
  }
}
```

**Job Pending Approval**:
```json
{
  "event": "job_pending_approval",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "pending_approval",
  "crew": "ContentCreationCrew",
  "created_at": "2023-06-15T12:34:56.789Z",
  "updated_at": "2023-06-15T12:38:32.123Z",
  "partial_result": {
    "content": "Artificial Intelligence (AI) refers to...",
    "awaiting_approval": true
  }
}
```

## Job States

A job can be in one of the following states:

- **queued**: Job has been created and is waiting to be processed
- **processing**: Job is currently being processed
- **pending_approval**: Job is waiting for human approval
- **completed**: Job has completed successfully
- **error**: Job encountered an error
- **cancelled**: Job was cancelled by the user

## Human-in-the-Loop Workflows

Human-in-the-Loop (HITL) workflows allow for human feedback and approval during the agent execution process. Here's a complete HITL workflow example:

1. **Start a job requiring approval**:
   ```bash
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Climate Change",
         "require_approval": true
       }
     }'
   ```

2. **Check job status until it's pending approval**:
   ```bash
   curl "https://content-agent.agentic.canary-orion.keboola.dev/job/YOUR_JOB_ID"
   ```

3. **Provide feedback or approve**:
   ```bash
   # To approve:
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/job/YOUR_JOB_ID/feedback" \
     -H "Content-Type: application/json" \
     -d '{
       "feedback": "Content approved as is.",
       "approved": true
     }'
   
   # To request changes:
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/job/YOUR_JOB_ID/feedback" \
     -H "Content-Type: application/json" \
     -d '{
       "feedback": "Please add more examples about renewable energy.",
       "approved": false
     }'
   ```

4. **If feedback was provided, check status again** until it's "pending_approval" again or "completed", then review the updated content.

## Environment Variables

When deploying your AI Agent Runtime using the Management API, you can configure environment variables that affect the runtime behavior.

### Required Variables for Common LLM Providers

#### OpenRouter (Default)

```json
"envVars": [
  {"name": "LLM_PROVIDER", "value": "openrouter"},
  {"name": "OPENAI_API_KEY", "value": "sk-...", "secure": true},
  {"name": "OPENROUTER_MODEL", "value": "openai/gpt-4o-mini"}
]
```

#### Azure OpenAI

```json
"envVars": [
  {"name": "LLM_PROVIDER", "value": "azure"},
  {"name": "AZURE_OPENAI_API_KEY", "value": "your-key", "secure": true},
  {"name": "AZURE_OPENAI_ENDPOINT", "value": "https://your-resource.openai.azure.com"},
  {"name": "AZURE_OPENAI_DEPLOYMENT_ID", "value": "gpt-35-turbo"},
  {"name": "AZURE_OPENAI_API_VERSION", "value": "2023-05-15"}
]
```

#### Anthropic Claude

```json
"envVars": [
  {"name": "LLM_PROVIDER", "value": "anthropic"},
  {"name": "ANTHROPIC_API_KEY", "value": "your-key", "secure": true},
  {"name": "ANTHROPIC_MODEL", "value": "claude-3-opus-20240229"}
]
```

## Troubleshooting

### Common Issues

#### 1. Job Stuck in "Processing" State

**Possible causes**:
- The agent is experiencing a long-running operation
- There might be an issue with the LLM API access
- The agent code has an error that's not being properly caught

**Solutions**:
- Check the runtime logs through the Management API
- Verify your API keys and rate limits with the LLM provider
- Restart the runtime using the Management API

#### 2. Job Returns Error Status

**Possible causes**:
- Invalid inputs provided to the crew
- Missing environment variables
- Errors in the agent code

**Solutions**:
- Check the `error_message` field in the job status response
- Verify all required environment variables are set
- Check the runtime logs for detailed error information

#### 3. Webhook Not Being Received

**Possible causes**:
- The webhook URL is not publicly accessible
- Network issues or firewall blocking the webhook requests
- Incorrect webhook URL format

**Solutions**:
- Ensure your webhook endpoint is publicly accessible
- Verify the URL format is correct (must include http:// or https://)
- Check the runtime logs for webhook delivery attempt errors

## Advanced Configuration

### API Server Configuration

When deploying your AI Agent Runtime, you can configure these environment variables:

```json
"envVars": [
  {"name": "API_HOST", "value": "0.0.0.0"},
  {"name": "API_PORT", "value": "80"},
  {"name": "API_LOG_LEVEL", "value": "info"},
  {"name": "API_WORKER_CONCURRENCY", "value": "5"}
]
```

### Job Storage Configuration

The runtime API supports different storage backends for job data:

```json
"envVars": [
  {"name": "JOB_STORAGE_TYPE", "value": "memory"},
  {"name": "JOB_RETENTION_DAYS", "value": "30"}
]
```

For PostgreSQL storage:

```json
"envVars": [
  {"name": "JOB_STORAGE_TYPE", "value": "postgres"},
  {"name": "POSTGRES_URL", "value": "postgresql://user:password@host:5432/dbname", "secure": true},
  {"name": "POSTGRES_MIN_CONNECTIONS", "value": "1"},
  {"name": "POSTGRES_MAX_CONNECTIONS", "value": "10"}
]
```

### Webhook Configuration

```json
"envVars": [
  {"name": "WEBHOOK_RETRY_ATTEMPTS", "value": "3"},
  {"name": "WEBHOOK_RETRY_DELAY", "value": "5"},
  {"name": "WEBHOOK_TIMEOUT", "value": "10"},
  {"name": "WEBHOOK_VERIFY_SSL", "value": "true"}
] 