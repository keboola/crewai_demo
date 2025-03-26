# AI Agent Runtime API

> [!NOTE]
> This documentation explains how to use the AI Agent Runtime API to interact with your deployed CrewAI agents on the AI Agent Platform.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Kickoff Endpoint](#kickoff-endpoint)
  - [Run Status](#run-status)
  - [Feedback Endpoint](#feedback-endpoint)
  - [List Runs](#list-runs)
  - [List Crews](#list-crews)
  - [Delete Run](#delete-run)
- [Webhook Notifications](#webhook-notifications)
- [Run States](#run-states)
- [Human-in-the-Loop Workflows](#human-in-the-loop-workflows)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

The AI Agent Runtime API provides a RESTful interface for interacting with your deployed CrewAI agents. Each AI Agent Runtime deployed through the Management API has its own API endpoint that enables:

- **Asynchronous execution** of CrewAI workflows
- **Human-in-the-Loop (HITL)** approval processes
- **Webhook notifications** for run status updates
- **Run tracking** across multiple executions
- **Crew discovery** to explore available agent crews

## Quick Start

Once you've deployed an AI Agent Runtime using the Management API, you can interact with it through its API:

1. **Find your runtime URL**:
   ```bash
   # If your runtime is named "content-agent"
   https://content-agent.agentic.canary-orion.keboola.dev
   ```

2. **Start your first run**:
   ```bash
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Artificial Intelligence"
       }
     }'
   ```

3. **Check run status** (using the run_id from the response):
   ```bash
   curl "https://content-agent.agentic.canary-orion.keboola.dev/run/987ca65a-62cf-4c48-850b-ad0eb3e37393" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN"
   ```

## Authentication

The Runtime API uses token-based authentication to secure access to the API endpoints. By default, authentication is enabled for all API endpoints except the health check.

### Making Authenticated Requests

When authentication is enabled, include your token in the Authorization header using the Bearer scheme:

```bash
curl -H "Authorization: Bearer YOUR_AUTH_TOKEN" https://content-agent.agentic.canary-orion.keboola.dev/endpoint
```

Replace `YOUR_AUTH_TOKEN` with the authentication token provided to your runtime during deployment. This is the same token used for the Management API.

### Authentication Configuration

Authentication is controlled by environment variables in the runtime:

- `API_AUTH_ENABLED`: Controls whether authentication is required (default: `true`)
- `API_AUTH_TOKEN`: The token that must be provided with requests

These variables are automatically configured by the platform when runtimes are deployed.

### Endpoints Exempt from Authentication

The following endpoints are accessible without authentication:

- `GET /health`: Health check endpoint

All other endpoints require authentication when it's enabled.

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
  "active_runs": 2,
  "version": "0.1.0"
}
```

### Kickoff Endpoint

**Endpoint**: `POST /kickoff`

Starts a new agent run.

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
- `webhook_url` (string, optional): URL to receive run status updates

**Example**:

```bash
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
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
  "run_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

### Run Status

**Endpoint**: `GET /run/{run_id}`

Retrieves the status and result of a specific run.

**Path Parameters**:
- `run_id`: ID of the run to retrieve

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/run/987ca65a-62cf-4c48-850b-ad0eb3e37393" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
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
  "updated_at": "2023-06-15T12:35:12.345Z",
  "webhook_status_sent": {
    "processing": true,
    "completed": false
  }
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
  "updated_at": "2023-06-15T12:35:12.345Z",
  "result": {
    "content": "Artificial Intelligence (AI) refers to...",
    "length": 1234
  }
}
```

### Feedback Endpoint

**Endpoint**: `POST /run/{run_id}/feedback`

Provides human feedback for a run that's pending approval.

**Path Parameters**:
- `run_id`: ID of the run to provide feedback for

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
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/run/987ca65a-62cf-4c48-850b-ad0eb3e37393/feedback" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "feedback": "Please make the content more concise and add more examples.",
    "approved": false
  }'
```

**Response (Not Approved)**:

```json
{
  "message": "Feedback recorded and content generation restarted with feedback",
  "run_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

### List Runs

**Endpoint**: `GET /runs`

Lists all runs with optional filtering.

**Query Parameters**:
- `limit` (integer, optional): Maximum number of runs to return (default: 10, max: 100)
- `status` (string, optional): Filter runs by status (e.g., "QUEUED", "PROCESSING", "COMPLETED", "ERROR", "PENDING_APPROVAL")

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/runs?limit=5&status=COMPLETED" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Response**:

```json
{
  "runs": [
    {
      "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
      "crew": "ContentCreationCrew",
      "status": "COMPLETED",
      "created_at": "2025-03-15T12:34:56.789Z",
      "completed_at": "2025-03-15T12:40:56.789Z",
      "has_result": true,
      "has_error": false
    },
    {
      "id": "123ab45c-78de-9f01-234g-h5i67j8klmno",
      "crew": "ResearchCrew",
      "status": "COMPLETED",
      "created_at": "2025-03-15T11:22:33.444Z",
      "completed_at": "2025-03-15T11:30:44.555Z",
      "has_result": true,
      "has_error": false
    }
  ],
  "count": 2,
  "limit": 5,
  "status_filter": "COMPLETED"
}
```

> [!NOTE]
> The response includes a summary of each run. To get the full details including results, use the `/run/{run_id}` endpoint.

### List Crews

**Endpoint**: `GET /list-crews`

Lists all available crews that can be used with the kickoff endpoint.

**Example**:

```bash
curl "https://content-agent.agentic.canary-orion.keboola.dev/list-crews" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
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

### Delete Run

**Endpoint**: `DELETE /run/{run_id}`

Deletes a run and its associated data.

**Path Parameters**:
- `run_id`: ID of the run to delete

**Example**:

```bash
curl -X DELETE "https://content-agent.agentic.canary-orion.keboola.dev/run/987ca65a-62cf-4c48-850b-ad0eb3e37393" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN"
```

**Response**:

```json
{
  "message": "Run deleted successfully",
  "run_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

## Webhook Notifications

The API can send webhook notifications to a URL you specify when a run's status changes. This is useful for implementing asynchronous workflows.

To use webhooks, include a `webhook_url` parameter when starting a run:

```bash
curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "brain_dump": "Artificial Intelligence"
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

### Webhook Payload Examples

**Run Created**:
```json
{
  "run_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
  "status": "queued",
  "crew": "ContentCreationCrew",
  "created_at": "2025-03-24T08:34:56.789Z",
  "meta": {
    "webhook_sent_at": "2025-03-24T08:34:56.973Z",
    "webhook_id": "whk_20250324083456_a1b2c3d4",
    "origin": {
      "platform": "AI Agent Platform",
      "runtime_id": "rt_2de04537c9e9",
      "runtime_name": "content-creation-agent-webhook",
      "api_url": "https://content-agent.agentic.canary-orion.keboola.dev",
      "environment": "production"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "run_RunStatus.QUEUED"
}
```

For more detailed webhook information, examples, and integration patterns, see the [Webhook Integration Guide](../guides/webhook-integration.md).

## Run States

A run can be in one of the following states:

- **queued**: Run has been created and is waiting to be processed
- **processing**: Run is currently being processed
- **pending_approval**: Run is waiting for human approval
- **completed**: Run has completed successfully
- **error**: Run encountered an error
- **cancelled**: Run was cancelled by the user

## Human-in-the-Loop Workflows

Human-in-the-Loop (HITL) workflows allow for human feedback and approval during the agent execution process. Here's a complete HITL workflow example:

1. **Start a run requiring approval**:
   ```bash
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Climate Change",
         "require_approval": true
       }
     }'
   ```

2. **Check run status until it's pending approval**:
   ```bash
   curl "https://content-agent.agentic.canary-orion.keboola.dev/run/YOUR_RUN_ID" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN"
   ```

3. **Provide feedback or approve**:
   ```bash
   # To approve:
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/run/YOUR_RUN_ID/feedback" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "feedback": "Content approved as is.",
       "approved": true
     }'
   
   # To request changes:
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/run/YOUR_RUN_ID/feedback" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
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

#### 1. Run Stuck in "Processing" State

**Possible causes**:
- The agent is experiencing a long-running operation
- There might be an issue with the LLM API access
- The agent code has an error that's not being properly caught

**Solutions**:
- Check the runtime logs through the Management API
- Verify your API keys and rate limits with the LLM provider
- Restart the runtime using the Management API

#### 2. Run Returns Error Status

**Possible causes**:
- Invalid inputs provided to the crew
- Missing environment variables
- Errors in the agent code

**Solutions**:
- Check the `error_message` field in the run status response
- Verify all required environment variables are set
- Check the runtime logs for detailed error information

For more troubleshooting help, see the [Troubleshooting Guide](../guides/troubleshooting.md).

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

### Run Storage Configuration

The runtime API supports different storage backends for run data:

```json
"envVars": [
  {"name": "RUN_STORAGE_TYPE", "value": "memory"},
  {"name": "RUN_RETENTION_DAYS", "value": "30"}
]
```

For PostgreSQL storage:

```json
"envVars": [
  {"name": "RUN_STORAGE_TYPE", "value": "postgres"},
  {"name": "POSTGRES_URL", "value": "postgresql://user:password@host:5432/dbname", "secure": true},
  {"name": "POSTGRES_MIN_CONNECTIONS", "value": "1"},
  {"name": "POSTGRES_MAX_CONNECTIONS", "value": "10"}
]
```

For more configuration options, see the [Configuration Guide](../guides/configuration.md).

Last Updated: March 26, 2025 