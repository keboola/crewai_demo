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
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Artificial Intelligence"
       }
     }'
   ```

3. **Check job status** (using the job_id from the response):
   ```bash
   curl "https://content-agent.agentic.canary-orion.keboola.dev/job/987ca65a-62cf-4c48-850b-ad0eb3e37393" \
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
  "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
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
      "environment": "production",
      "hostname": "content-creation-agent-webhook-7c8bbb976c-8qptf"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "job_JobStatus.QUEUED"
}
```

**Job Processing**:
```json
{
  "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
  "status": "processing",
  "crew": "ContentCreationCrew",
  "created_at": "2025-03-24T08:34:56.789Z",
  "meta": {
    "webhook_sent_at": "2025-03-24T08:35:12.345Z",
    "webhook_id": "whk_20250324083512_b2c3d4e5",
    "origin": {
      "platform": "AI Agent Platform",
      "runtime_id": "rt_2de04537c9e9",
      "runtime_name": "content-creation-agent-webhook",
      "api_url": "https://content-agent.agentic.canary-orion.keboola.dev",
      "environment": "production",
      "hostname": "content-creation-agent-webhook-7c8bbb976c-8qptf"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "job_JobStatus.PROCESSING"
}
```

**Job Completed**:
```json
{
  "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
  "status": "completed",
  "crew": "ContentCreationCrew",
  "completed_at": "2025-03-24T08:38:32.576961",
  "result": {
    "status": "success",
    "content": "# The Allure of Spring Onions: A Comprehensive Guide\n\n## 1. Introduction\nSpring onions, often referred to as scallions, green onions, or bunching onions...",
    "length": 5754,
    "timestamp": "2025-03-24T08:38:32.576877",
    "feedback_incorporated": false
  },
  "meta": {
    "webhook_sent_at": "2025-03-24T08:38:32.577207",
    "webhook_id": "whk_20250324083832_5507163c",
    "origin": {
      "platform": "AI Agent Platform",
      "runtime_id": "rt_2de04537c9e9",
      "runtime_name": "content-creation-agent-webhook",
      "api_url": "https://content-agent.agentic.canary-orion.keboola.dev",
      "environment": "production",
      "hostname": "content-creation-agent-webhook-7c8bbb976c-8qptf"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "job_JobStatus.COMPLETED"
}
```

**Job Pending Approval**:
```json
{
  "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
  "status": "pending_approval",
  "crew": "ContentCreationCrew",
  "created_at": "2025-03-24T08:34:56.789Z",
  "updated_at": "2025-03-24T08:36:32.123Z",
  "partial_result": {
    "status": "awaiting_approval",
    "content": "# The Allure of Spring Onions: A Comprehensive Guide\n\n## 1. Introduction\nSpring onions, often referred to as scallions, green onions, or bunching onions...",
    "length": 5500,
    "approval_message": "Please review this article before final publication"
  },
  "meta": {
    "webhook_sent_at": "2025-03-24T08:36:32.345Z",
    "webhook_id": "whk_20250324083632_c3d4e5f6",
    "origin": {
      "platform": "AI Agent Platform",
      "runtime_id": "rt_2de04537c9e9",
      "runtime_name": "content-creation-agent-webhook",
      "api_url": "https://content-agent.agentic.canary-orion.keboola.dev",
      "environment": "production",
      "hostname": "content-creation-agent-webhook-7c8bbb976c-8qptf"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "job_JobStatus.PENDING_APPROVAL"
}
```

**Job Error**:
```json
{
  "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
  "status": "error",
  "crew": "ContentCreationCrew",
  "created_at": "2025-03-24T08:34:56.789Z",
  "error_message": "LLM provider returned an error: Rate limit exceeded",
  "meta": {
    "webhook_sent_at": "2025-03-24T08:39:12.345Z",
    "webhook_id": "whk_20250324083912_d4e5f6g7",
    "origin": {
      "platform": "AI Agent Platform",
      "runtime_id": "rt_2de04537c9e9",
      "runtime_name": "content-creation-agent-webhook",
      "api_url": "https://content-agent.agentic.canary-orion.keboola.dev",
      "environment": "production",
      "hostname": "content-creation-agent-webhook-7c8bbb976c-8qptf"
    },
    "version": {
      "platform_version": "0.1.0"
    },
    "spec_version": "1.0"
  },
  "event": "job_JobStatus.ERROR"
}
```

### Webhook Metadata Fields

Our webhooks include useful metadata to help you manage and troubleshoot your integrations:

- **meta.webhook_sent_at**: Timestamp when the webhook was sent (useful for monitoring delivery times)
- **meta.webhook_id**: Unique identifier for this specific webhook notification
  - Useful for deduplication if a webhook is sent multiple times due to retry attempts
  - Helpful for tracking webhook delivery in your logs
  - Can be referenced when contacting support about webhook issues
  - Stored in the job's webhook history for future reference
- **meta.origin**: Information about the source of the webhook:
  - **platform**: Always "AI Agent Platform"
  - **runtime_id**: The unique identifier for the runtime instance that sent the webhook
    - This is a permanent, stable identifier that persists across restarts
    - Use this ID when referencing the runtime in API calls to the Management API
  - **runtime_name**: A human-readable name of the runtime (e.g., "content-creation-agent")
    - Use this for display purposes in dashboards or logs
    - Can be configured with the RUNTIME_NAME environment variable
  - **api_url**: The base URL where the runtime's API is accessible
    - This is the most critical field for constructing follow-up API calls
    - Uses the INGRESS_HOST environment variable if set (recommended for production)
    - Falls back to internal service URL if INGRESS_HOST is not set
    - Use this to build URLs for job status, feedback, or cancellation requests
  - **environment**: The deployment environment (production, staging, etc.)
  - **hostname**: The hostname of the server that sent the webhook (mostly for debugging)
- **meta.version**: Version information for the platform
  - **platform_version**: The version of the AI Agent Platform
    - Important for troubleshooting compatibility issues
    - Reference this version when reporting bugs or issues
- **meta.spec_version**: Version of the webhook specification format
  - Helps you understand the structure of the webhook payload
  - Will increment if we make breaking changes to the webhook format

For best results, make sure to set the following environment variables in your runtime to ensure accurate webhook metadata:
- **INGRESS_HOST**: The public hostname where your runtime can be accessed (e.g., "content-agent.agentic.example.com")
- **RUNTIME_NAME**: A human-readable name for your runtime (e.g., "content-creation-agent")
- **API_URL**: Only set this if INGRESS_HOST cannot be used

The runtime will store a history of all webhooks sent for each job, which you can access through the job status endpoint. This history includes:
- Webhook ID
- Status update that triggered the webhook
- Timestamp when it was sent
- Destination URL

### Practical Uses for Webhook Metadata

Here are some common ways to use the webhook metadata in your integration:

1. **Building follow-up API calls**:
   ```python
   # When receiving a webhook that a job is pending approval
   import requests
   
   def handle_webhook(webhook_data):
       # Extract metadata from webhook
       api_url = webhook_data['meta']['origin']['api_url']
       job_id = webhook_data['job_id']
       
       # Check the event type - note the format "job_JobStatus.XXX"
       event = webhook_data['event']
       
       # Handle different event types
       if event == 'job_JobStatus.PENDING_APPROVAL':
           # Construct URL for providing feedback
           feedback_url = f"{api_url}/job/{job_id}/feedback"
           
           # Later, send approval via this URL
           response = requests.post(
               feedback_url,
               json={
                   "feedback": "Content looks good!",
                   "approved": True
               },
               headers={"Authorization": f"Bearer {YOUR_AUTH_TOKEN}"}
           )
           
           return response.json()
   ```

2. **Deduplication and idempotency**:
   ```python
   # Store processed webhook IDs to avoid duplicate processing
   processed_webhooks = set()
   
   def handle_webhook(webhook_data):
       webhook_id = webhook_data['meta']['webhook_id']
       
       # Skip if already processed
       if webhook_id in processed_webhooks:
           print(f"Webhook {webhook_id} already processed, skipping")
           return
       
       # Process the webhook...
       process_job_update(webhook_data)
       
       # Mark as processed
       processed_webhooks.add(webhook_id)
       
       # In a production system, you would persist this to a database
       # Example with Redis:
       # import redis
       # r = redis.Redis()
       # r.sadd("processed_webhooks", webhook_id)
   
   # When checking if a webhook was processed:
   # was_processed = r.sismember("processed_webhooks", webhook_id)
   ```

3. **Monitoring and troubleshooting**:
   ```python
   import datetime
   
   def log_webhook(webhook_data):
       runtime_name = webhook_data['meta']['origin']['runtime_name']
       runtime_id = webhook_data['meta']['origin']['runtime_id']
       event = webhook_data['event']  # Format will be "job_JobStatus.XXX"
       status = webhook_data['status'] # Direct status field (e.g., "completed")
       job_id = webhook_data['job_id']
       sent_at = webhook_data['meta']['webhook_sent_at']
       platform_version = webhook_data['meta']['version']['platform_version']
       
       print(f"Webhook received from {runtime_name} ({runtime_id})")
       print(f"Event: {event}, Status: {status}, Job: {job_id}")
       print(f"Sent at: {sent_at}")
       print(f"Platform version: {platform_version}")
       
       # Calculate webhook delivery delay
       sent_time = datetime.datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
       received_time = datetime.datetime.now(datetime.timezone.utc)
       delay_seconds = (received_time - sent_time).total_seconds()
       print(f"Delivery delay: {delay_seconds:.3f} seconds")
       
       # Check for public API URL (should not be internal)
       api_url = webhook_data['meta']['origin']['api_url']
       if any(x in api_url for x in ['localhost', '0.0.0.0', '127.0.0.1']):
           print(f"WARNING: API URL {api_url} appears to be an internal URL")
   ```

4. **Accessing webhook history**:
   ```python
   import requests
   
   def get_webhook_history(api_url, job_id, auth_token):
       """Retrieves the webhook notification history for a job"""
       job_url = f"{api_url}/job/{job_id}"
       
       response = requests.get(
           job_url,
           headers={"Authorization": f"Bearer {auth_token}"}
       )
       
       job_data = response.json()
       
       # Get webhook history if available
       webhook_history = job_data.get('webhook_history', [])
       
       if webhook_history:
           print(f"Found {len(webhook_history)} webhook notifications for job {job_id}:")
           for webhook in webhook_history:
               print(f"  ID: {webhook['webhook_id']}")
               print(f"  Status: {webhook['status']}")
               print(f"  Sent at: {webhook['sent_at']}")
               print(f"  URL: {webhook['url']}")
               print()
       else:
           print(f"No webhook history found for job {job_id}")
           
       return webhook_history
   ```

5. **Creating a Flask webhook receiver**:
   ```python
   from flask import Flask, request, jsonify
   
   app = Flask(__name__)
   
   @app.route('/webhook', methods=['POST'])
   def receive_webhook():
       if not request.json:
           return jsonify({"error": "Invalid JSON"}), 400
       
       webhook_data = request.json
       
       # Extract the status from the event string or use the status field
       event = webhook_data['event']
       status = webhook_data['status']
       
       # Log the webhook
       print(f"Received webhook: {event} for job {webhook_data['job_id']}")
       
       # Store webhook_id for deduplication
       webhook_id = webhook_data['meta']['webhook_id']
       print(f"Webhook ID: {webhook_id}")
       
       # Process based on status or event type
       if status == 'completed':
           # Handle completed job
           process_completed_job(webhook_data)
       elif status == 'pending_approval':
           # Handle job needing approval
           process_pending_approval(webhook_data)
       elif status == 'error':
           # Handle job error
           process_job_error(webhook_data)
       
       return jsonify({"status": "success"}), 200
   
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000)
   ```

### Testing Webhooks

To help you test webhook functionality, we provide a simple webhook receiver script. You can use this to quickly set up a webhook server for development and testing.

1. **Run the webhook server**:

   From the AI Agent Platform repository:
   ```bash
   # From repository root
   python scripts/tools/webhook_server.py --host 0.0.0.0 --port 8889
   ```

   Or directly from your code directory:
   ```bash
   # Copy the script from the repository or download it
   wget https://raw.githubusercontent.com/keboola/agentic-platform/main/scripts/tools/webhook_server.py
   python webhook_server.py --host 0.0.0.0 --port 8889
   ```

   This will start a webhook receiver on port 8889 and print:
   ```
   Starting webhook receiver on http://0.0.0.0:8889
   Webhook URL: http://0.0.0.0:8889/webhook
   View received webhooks at: http://0.0.0.0:8889/
   Clear webhooks at: http://0.0.0.0:8889/clear
   ```

2. **Make the webhook endpoint accessible**:
   
   If you're testing locally, you'll need to use a service like [ngrok](https://ngrok.com/) or [localtunnel](https://github.com/localtunnel/localtunnel) to expose your local server to the internet:

   ```bash
   # Using ngrok
   ngrok http 8889
   
   # Using localtunnel
   npx localtunnel --port 8889
   ```

   This will give you a public URL like `https://1234abcd.ngrok.io` that you can use as your webhook URL.

3. **Configure your job with the webhook URL**:

   ```bash
   curl -X POST "https://content-agent.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "brain_dump": "Artificial Intelligence"
       },
       "webhook_url": "https://1234abcd.ngrok.io/webhook"
     }'
   ```

4. **View received webhooks**:

   - In your terminal running the webhook server, you'll see the webhook data printed as it's received
   - You can also visit `http://localhost:8889/` in your browser to see all received webhooks
   - Use `http://localhost:8889/latest?count=5` to see the 5 most recent webhooks
   - Clear all webhooks with `http://localhost:8889/clear`

5. **Understanding webhook server output**:

   When using the included webhook server, you'll notice two types of output for each webhook:
   
   ```
   2025-03-24 09:38:33,759 - webhook_server - INFO - Webhook received: {
     "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
     "status": "completed",
     ...
   }
   
   === Webhook Received at 2025-03-24T09:38:33.758891 ===
   {
     "job_id": "125ce79b-3373-4dd0-be5e-9b49b4391fb5",
     "status": "completed",
     ...
   }
   ```
   
   The first part is the Python logger output, and the second part (with the `===` header) is from a print statement for console visibility. Both show the same webhook - you're not receiving duplicate webhooks.

   The HTTP status lines (e.g., `INFO: 127.0.0.1:54676 - "POST /webhook HTTP/1.1" 200 OK`) indicate successful HTTP requests being processed.

This webhook server is perfect for development and testing, but for production use, you should implement a more robust webhook receiver with proper error handling, authentication, and persistence.

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