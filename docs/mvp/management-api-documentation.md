# AI Agent Platform Management API

> [!NOTE]
> This documentation outlines the Management API for the AI Agent Platform, which allows AI engineers to deploy and manage their CrewAI agents on Kubernetes.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [AI Agent Runtimes](#ai-agent-runtimes)
  - [Environment Variables](#environment-variables)
  - [Code Management](#code-management)
  - [Runtime Operations](#runtime-operations)
  - [Runtime Monitoring](#runtime-monitoring)
  - [Agent Management](#agent-management)
  - [Token Management](#token-management)
- [Request and Response Models](#request-and-response-models)
- [Implementation Examples](#implementation-examples)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Further Resources](#further-resources)

## Overview

The AI Agent Platform Management API provides a user-friendly interface for creating and managing AI Agent Runtimes. It acts as a bridge between users and the underlying Kubernetes infrastructure, translating user-friendly requests into Kubernetes Custom Resources that are processed by the platform's operator.

Key features:

- **Simple Deployment**: Deploy CrewAI agents with minimal configuration
- **Code Management**: Upload code directly or integrate with GitHub repositories
- **Environment Management**: Configure environment variables for your agents
- **Scalability**: Control resource allocation and replica count
- **Operations**: Start, stop, and monitor your deployed agents

## Quick Start

<details>
<summary>Click to expand quick start instructions</summary>

1. **Set up authentication**:

   ```bash
   # Get your API key from the platform dashboard
   export AI_PLATFORM_API_KEY="your-api-key"
   ```

2. **Deploy your first agent**:

   ```bash
   curl -X POST https://api.ai-agent-platform.example.com/api/runtimes \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
     -d '{
       "name": "my-first-agent",
       "description": "My first CrewAI agent",
       "entrypoint": "crewai_app/orchestrator.py",
       "code_source": {
         "type": "github",
         "gitRepo": {
           "url": "https://github.com/username/my-crewai-project",
           "branch": "main"
         }
       },
       "env_vars": [
         {
           "name": "OPENAI_API_KEY",
           "value": "sk-..."
         }
       ]
     }'
   ```

3. **Check deployment status**:

   ```bash
   curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/my-first-agent \
     -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
   ```

</details>

## Authentication

The Management API uses JWT-based authentication. All requests must include an Authorization header with a valid Bearer token.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes \
  -H "Authorization: Bearer your-token-here"
```

### Runtime API Authentication

For accessing Runtime APIs, you'll need to request a separate token from the Management API using the token management endpoints. This allows direct communication with Runtime APIs without routing through the Management API.

```bash
# First, get a token for a specific runtime
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/tokens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "description": "Development access",
    "duration": "24h",
    "permissions": ["read", "execute"]
  }'

# Use the returned token to access the Runtime API directly
curl -X POST https://content-generation-agent.ai-platform.example.com/kickoff \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${RUNTIME_ACCESS_TOKEN}" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Artificial Intelligence"
    }
  }'
```

## API Endpoints

### AI Agent Runtimes

#### Create a New Runtime

**Endpoint**: `POST /api/runtimes`

Creates a new AI Agent Runtime deployment.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "name": "content-generation-agent",
    "description": "Agent for generating blog content",
    "entrypoint": "crewai_app/orchestrator.py",
    "code_source": {
      "type": "github",
      "gitRepo": {
        "url": "https://github.com/username/content-generation-crew",
        "branch": "main"
      }
    },
    "env_vars": [
      {
        "name": "OPENAI_API_KEY",
        "value": "sk-..."
      },
      {
        "name": "WEBHOOK_URL",
        "value": "https://my-service.example.com/webhook"
      }
    ],
    "resources": {
      "requests": {
        "cpu": "100m",
        "memory": "256Mi"
      },
      "limits": {
        "cpu": "500m",
        "memory": "512Mi"
      }
    },
    "network_policy": {
      "internet_access": true,
      "allowed_domains": ["api.openai.com", "api.anthropic.com", "huggingface.co"],
      "allowed_ips": [],
      "egress_rules": []
    },
    "replicas": 1
  }'
```

</details>

**Parameters**:

- `name` (string): Unique name for the runtime
- `description` (string, optional): Human-readable description
- `entrypoint` (string): Path to the entry Python file
- `code_source` (object): Source of the code (GitHub, direct upload, etc.)
- `env_vars` (array, optional): Environment variables for the runtime
- `resources` (object, optional): CPU and memory requests/limits
- `network_policy` (object, optional): Network access controls for the runtime
  - `internet_access` (boolean, optional): Whether to allow unrestricted internet access (default: true)
  - `allowed_domains` (array, optional): List of domains to whitelist when internet access is restricted
  - `allowed_ips` (array, optional): List of IP addresses or CIDR blocks to whitelist
  - `egress_rules` (array, optional): Advanced Kubernetes NetworkPolicy egress rules
- `replicas` (integer, optional): Number of replica pods (default: 1)
- `db_config` (object, optional): Database configuration if required

<details>
<summary>Click to see response example</summary>

```json
{
  "name": "content-generation-agent",
  "namespace": "user-namespace",
  "status": {
    "phase": "Pending",
    "message": "Creating deployment",
    "lastTransitionTime": "2023-07-15T12:34:56.789012Z"
  },
  "spec": {
    "name": "content-generation-agent",
    "description": "Agent for generating blog content",
    "entrypoint": "crewai_app/orchestrator.py",
    "code_source": {
      "type": "github",
      "gitRepo": {
        "url": "https://github.com/username/content-generation-crew",
        "branch": "main"
      }
    },
    "env_vars": [
      {
        "name": "OPENAI_API_KEY",
        "value": "sk-..."
      },
      {
        "name": "WEBHOOK_URL",
        "value": "https://my-service.example.com/webhook"
      }
    ],
    "resources": {
      "requests": {
        "cpu": "100m",
        "memory": "256Mi"
      },
      "limits": {
        "cpu": "500m",
        "memory": "512Mi"
      }
    },
    "network_policy": {
      "internet_access": true,
      "allowed_domains": ["api.openai.com", "api.anthropic.com", "huggingface.co"],
      "allowed_ips": []
    },
    "replicas": 1
  }
}
```

</details>

#### List All Runtimes

**Endpoint**: `GET /api/runtimes`

Returns a list of all AI Agent Runtimes accessible to the authenticated user.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtimes": [
    {
      "name": "content-generation-agent",
      "description": "Agent for generating blog content",
      "framework": "CrewAI",
      "access": {
        "url": "https://content-generation-agent.ai-platform.example.com",
        "api_docs": "https://content-generation-agent.ai-platform.example.com/docs",
        "status": "Running"
      },
      "created_at": "2023-07-15T12:34:56.789012Z",
      "status": {
        "phase": "Running",
        "lastTransitionTime": "2023-07-15T12:40:56.789012Z"
      }
    },
    {
      "name": "research-assistant",
      "description": "Agent for researching topics",
      "framework": "CrewAI",
      "access": {
        "url": "https://research-assistant.ai-platform.example.com",
        "api_docs": "https://research-assistant.ai-platform.example.com/docs",
        "status": "Running"
      },
      "created_at": "2023-07-14T15:20:11.222333Z",
      "status": {
        "phase": "Running",
        "lastTransitionTime": "2023-07-14T15:22:33.444555Z"
      }
    }
  ],
  "count": 2,
  "total": 2
}
```

</details>

#### Get Runtime Details

**Endpoint**: `GET /api/runtimes/{name}`

Retrieves detailed information about a specific AI Agent Runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "name": "content-generation-agent",
  "description": "Agent for generating blog content",
  "framework": "CrewAI",
  "access": {
    "url": "https://content-generation-agent.ai-platform.example.com",
    "api_docs": "https://content-generation-agent.ai-platform.example.com/docs",
    "status": "Running"
  },
  "namespace": "user-namespace",
  "status": {
    "phase": "Running",
    "message": "Deployment is ready",
    "lastTransitionTime": "2023-07-15T12:40:56.789012Z",
    "endpoint": "https://content-generation-agent.ai-platform.example.com",
    "availableReplicas": 1,
    "conditions": [
      {
        "type": "Available",
        "status": "True",
        "lastTransitionTime": "2023-07-15T12:40:56.789012Z"
      }
    ]
  },
  "spec": {
    "name": "content-generation-agent",
    "description": "Agent for generating blog content",
    "entrypoint": "crewai_app/orchestrator.py",
    "code_source": {
      "type": "github",
      "gitRepo": {
        "url": "https://github.com/username/content-generation-crew",
        "branch": "main"
      }
    },
    "env_vars": [
      {
        "name": "OPENAI_API_KEY",
        "value": "sk-..."
      },
      {
        "name": "WEBHOOK_URL",
        "value": "https://my-service.example.com/webhook"
      }
    ],
    "resources": {
      "requests": {
        "cpu": "100m",
        "memory": "256Mi"
      },
      "limits": {
        "cpu": "500m",
        "memory": "512Mi"
      }
    },
    "network_policy": {
      "internet_access": true,
      "allowed_domains": ["api.openai.com", "api.anthropic.com", "huggingface.co"],
      "allowed_ips": []
    },
    "replicas": 1
  },
  "created_at": "2023-07-15T12:34:56.789012Z",
  "updated_at": "2023-07-15T12:40:56.789012Z",
  "runtime_metrics": {
    "jobs_total": 15,
    "jobs_active": 2,
    "cpu_usage": "125m",
    "memory_usage": "156Mi"
  }
}
```

</details>

#### Delete Runtime

**Endpoint**: `DELETE /api/runtimes/{name}`

Deletes an AI Agent Runtime and all associated resources.

```bash
curl -X DELETE https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Runtime deletion initiated",
  "name": "content-generation-agent"
}
```

</details>

### Environment Variables

#### Add or Update Environment Variables

**Endpoint**: `POST /api/runtimes/{name}/environment`

Adds or updates environment variables for a specific runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/environment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "env_vars": [
      {
        "name": "OPENAI_API_KEY",
        "value": "sk-new-key"
      },
      {
        "name": "DEBUG_MODE",
        "value": "true"
      }
    ]
  }'
```

</details>

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Environment variables updated",
  "runtime_name": "content-generation-agent",
  "updated_vars": ["OPENAI_API_KEY", "DEBUG_MODE"]
}
```

</details>

#### Get Environment Variables

**Endpoint**: `GET /api/runtimes/{name}/environment`

Retrieves all environment variables for a specific runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/environment \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "env_vars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-..."
    },
    {
      "name": "WEBHOOK_URL",
      "value": "https://my-service.example.com/webhook"
    },
    {
      "name": "DEBUG_MODE",
      "value": "true"
    }
  ]
}
```

</details>

#### Update Specific Environment Variables

**Endpoint**: `PATCH /api/runtimes/{name}/environment`

Updates specific environment variables for a runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X PATCH https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/environment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "env_vars": [
      {
        "name": "DEBUG_MODE",
        "value": "false"
      }
    ]
  }'
```

</details>

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Environment variables updated",
  "runtime_name": "content-generation-agent",
  "updated_vars": ["DEBUG_MODE"]
}
```

</details>

#### Delete Environment Variable

**Endpoint**: `DELETE /api/runtimes/{name}/environment/{var_name}`

Removes a specific environment variable from a runtime.

```bash
curl -X DELETE https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/environment/DEBUG_MODE \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Environment variable deleted",
  "runtime_name": "content-generation-agent",
  "var_name": "DEBUG_MODE"
}
```

</details>

### Code Management

#### Upload Code Archive

**Endpoint**: `POST /api/runtimes/{name}/code/archive`

Uploads a code archive (ZIP, TAR, TAR.GZ) for a runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/code/archive \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -H "Content-Type: multipart/form-data" \
  -F "archive=@./my-agent-code.zip" \
  -F "archive_type=zip" \
  -F "extract_directory=/"
```

</details>

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Code archive uploaded and deployed",
  "runtime_name": "content-generation-agent",
  "archive_type": "zip",
  "files_count": 8
}
```

</details>

#### Upload Single File

**Endpoint**: `POST /api/runtimes/{name}/code/file`

Uploads a single file to a runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/code/file \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./orchestrator.py" \
  -F "filename=crewai_app/orchestrator.py" \
  -F "content_type=text/x-python"
```

</details>

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "File uploaded and deployed",
  "runtime_name": "content-generation-agent",
  "filename": "crewai_app/orchestrator.py"
}
```

</details>

#### Connect GitHub Repository

**Endpoint**: `POST /api/runtimes/{name}/code/github`

Connects a GitHub repository to a runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/code/github \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "url": "https://github.com/username/content-generation-crew",
    "branch": "main",
    "auth": {
      "type": "token",
      "token": "github-token"
    }
  }'
```

</details>

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "GitHub repository connected and code deployed",
  "runtime_name": "content-generation-agent",
  "repository": "https://github.com/username/content-generation-crew",
  "branch": "main"
}
```

</details>

#### Get Code Metadata

**Endpoint**: `GET /api/runtimes/{name}/code`

Retrieves metadata about the code currently deployed for a runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/code \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "code_source": {
    "type": "github",
    "gitRepo": {
      "url": "https://github.com/username/content-generation-crew",
      "branch": "main"
    }
  },
  "last_updated": "2023-07-15T12:34:56.789012Z",
  "files_count": 12,
  "entrypoint": "crewai_app/orchestrator.py"
}
```

</details>

#### Delete Code

**Endpoint**: `DELETE /api/runtimes/{name}/code`

Deletes all code associated with a runtime.

```bash
curl -X DELETE https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/code \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Code deleted",
  "runtime_name": "content-generation-agent"
}
```

</details>

### Runtime Operations

#### Start Runtime

**Endpoint**: `POST /api/runtimes/{name}/start`

Starts a stopped runtime.

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/start \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Runtime start initiated",
  "runtime_name": "content-generation-agent"
}
```

</details>

#### Stop Runtime

**Endpoint**: `POST /api/runtimes/{name}/stop`

Stops a running runtime.

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/stop \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Runtime stop initiated",
  "runtime_name": "content-generation-agent"
}
```

</details>

#### Restart Runtime

**Endpoint**: `POST /api/runtimes/{name}/restart`

Restarts a runtime.

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/restart \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Runtime restart initiated",
  "runtime_name": "content-generation-agent"
}
```

</details>

#### Get Runtime Status

**Endpoint**: `GET /api/runtimes/{name}/status`

Retrieves the current status of a runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/status \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "status": {
    "phase": "Running",
    "message": "Deployment is ready",
    "lastTransitionTime": "2023-07-15T12:40:56.789012Z",
    "endpoint": "https://content-generation-agent.ai-platform.example.com",
    "availableReplicas": 1,
    "conditions": [
      {
        "type": "Available",
        "status": "True",
        "lastTransitionTime": "2023-07-15T12:40:56.789012Z"
      }
    ]
  },
  "pods": [
    {
      "name": "content-generation-agent-5d8f7c9b68-abcd1",
      "status": "Running",
      "ready": true,
      "restarts": 0,
      "created_at": "2023-07-15T12:35:22.111222Z"
    }
  ]
}
```

</details>

#### Get Runtime Logs

**Endpoint**: `GET /api/runtimes/{name}/logs`

Retrieves logs for a runtime.

```bash
curl -X GET "https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/logs?container=agent&tail=100" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

**Query Parameters**:

- `container` (string, optional): Container name (default: "agent")
- `tail` (integer, optional): Number of lines to return (default: 100)
- `since` (string, optional): Return logs since this time (e.g., "1h", "2d")

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "container": "agent",
  "logs": [
    {
      "timestamp": "2023-07-15T12:35:30.123456Z",
      "message": "Starting AI Agent Runtime..."
    },
    {
      "timestamp": "2023-07-15T12:35:31.234567Z",
      "message": "Loading module from crewai_app/orchestrator.py"
    },
    {
      "timestamp": "2023-07-15T12:35:32.345678Z",
      "message": "Found CrewBase class: ContentCreationCrew"
    },
    {
      "timestamp": "2023-07-15T12:35:33.456789Z",
      "message": "API server started at http://0.0.0.0:8888"
    }
  ]
}
```

</details>

#### Tail Runtime Logs

**Endpoint**: `GET /api/runtimes/{name}/logs/tail`

Streams logs in real-time for a runtime.

```bash
curl -X GET "https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/logs/tail?since=2023-07-15T12:35:30Z" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

**Query Parameters**:

- `container` (string, optional): Container name (default: "agent")
- `since` (string, optional): ISO 8601 timestamp to start from
- `follow` (boolean, optional): Whether to follow the logs stream (default: true)

<details>
<summary>Click to see response example</summary>

```
This endpoint returns a stream of log events, one per line:

{"timestamp":"2023-07-15T12:35:34.567890Z","message":"Processing job 987ca65a-62cf-4c48-850b-ad0eb3e37393"}
{"timestamp":"2023-07-15T12:35:35.678901Z","message":"Job started for crew ContentCreationCrew"}
{"timestamp":"2023-07-15T12:35:36.789012Z","message":"Agent 'researcher' starting task..."}
...
```

</details>

#### Get Runtime Events

**Endpoint**: `GET /api/runtimes/{name}/events`

Retrieves Kubernetes events related to a runtime.

```bash
curl -X GET "https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/events" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "events": [
    {
      "type": "Normal",
      "reason": "Created",
      "message": "Created container agent",
      "timestamp": "2023-07-15T12:34:56.789012Z",
      "count": 1
    },
    {
      "type": "Normal",
      "reason": "Started",
      "message": "Started container agent",
      "timestamp": "2023-07-15T12:34:58.789012Z",
      "count": 1
    },
    {
      "type": "Warning",
      "reason": "Unhealthy",
      "message": "Liveness probe failed",
      "timestamp": "2023-07-15T12:40:30.789012Z",
      "count": 3
    }
  ]
}
```

</details>

### Token Management

#### Create Token

**Endpoint**: `POST /api/runtimes/{name}/tokens`

Creates a new access token for a specific runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/tokens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "description": "Development access token",
    "duration": "24h",
    "permissions": ["read", "execute"]
  }'
```

</details>

**Parameters**:

- `description` (string): Human-readable description of the token's purpose
- `duration` (string, optional): Duration for which the token is valid (e.g., "1h", "30d") (default: "24h")
- `permissions` (array, optional): List of permissions granted to this token (default: ["read", "execute"])

<details>
<summary>Click to see response example</summary>

```json
{
  "token_id": "t-12345abc",
  "description": "Development access token",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_at": "2023-07-16T12:34:56.789012Z",
  "created_at": "2023-07-15T12:34:56.789012Z",
  "permissions": ["read", "execute"]
}
```

</details>

#### List Tokens

**Endpoint**: `GET /api/runtimes/{name}/tokens`

Lists all tokens for a specific runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/tokens \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "tokens": [
    {
      "token_id": "t-12345abc",
      "description": "Development access token",
      "expires_at": "2023-07-16T12:34:56.789012Z",
      "created_at": "2023-07-15T12:34:56.789012Z",
      "created_by": "user-789",
      "permissions": ["read", "execute"],
      "last_used": "2023-07-15T13:22:10.123456Z"
    },
    {
      "token_id": "t-67890def",
      "description": "CI/CD integration",
      "expires_at": "2023-08-14T09:12:34.567890Z",
      "created_at": "2023-07-15T09:12:34.567890Z",
      "created_by": "user-789",
      "permissions": ["read", "execute"],
      "last_used": null
    }
  ],
  "count": 2
}
```

</details>

#### Revoke Token

**Endpoint**: `DELETE /api/runtimes/{name}/tokens/{token_id}`

Revokes a specific token immediately.

```bash
curl -X DELETE https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/tokens/t-12345abc \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Token revoked successfully",
  "token_id": "t-12345abc"
}
```

</details>

#### Refresh Token

**Endpoint**: `POST /api/runtimes/{name}/tokens/refresh`

Refreshes an existing token, extending its lifetime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/tokens/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "token_id": "t-12345abc",
    "duration": "24h"
  }'
```

</details>

**Parameters**:

- `token_id` (string): ID of the token to refresh
- `duration` (string, optional): New duration for the token (e.g., "1h", "30d") (default: "24h")

<details>
<summary>Click to see response example</summary>

```json
{
  "token_id": "t-12345abc",
  "description": "Development access token",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_at": "2023-07-17T12:34:56.789012Z",
  "created_at": "2023-07-15T12:34:56.789012Z",
  "refreshed_at": "2023-07-16T12:34:56.789012Z",
  "permissions": ["read", "execute"]
}
```

</details>

### Network Policy Management

#### Update Network Policy

**Endpoint**: `PATCH /api/runtimes/{name}/network-policy`

Updates the network access policy for a specific runtime.

<details>
<summary>Click to see request example</summary>

```bash
curl -X PATCH https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/network-policy \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}" \
  -d '{
    "internet_access": false,
    "allowed_domains": [
      "api.openai.com",
      "api.anthropic.com",
      "huggingface.co",
      "data.example.com"
    ],
    "allowed_ips": ["203.0.113.0/24"]
  }'
```

</details>

**Parameters**:
- `internet_access` (boolean, optional): Whether to allow unrestricted internet access
- `allowed_domains` (array, optional): List of domains to whitelist when internet access is restricted
- `allowed_ips` (array, optional): List of IP addresses or CIDR blocks to whitelist
- `egress_rules` (array, optional): Advanced Kubernetes NetworkPolicy egress rules

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Network policy updated",
  "runtime_name": "content-generation-agent",
  "network_policy": {
    "internet_access": false,
    "allowed_domains": [
      "api.openai.com",
      "api.anthropic.com",
      "huggingface.co",
      "data.example.com"
    ],
    "allowed_ips": ["203.0.113.0/24"],
    "egress_rules": []
  }
}
```

</details>

#### Get Network Policy

**Endpoint**: `GET /api/runtimes/{name}/network-policy`

Retrieves the current network policy for a specific runtime.

```bash
curl -X GET https://api.ai-agent-platform.example.com/api/runtimes/content-generation-agent/network-policy \
  -H "Authorization: Bearer ${AI_PLATFORM_API_KEY}"
```

<details>
<summary>Click to see response example</summary>

```json
{
  "runtime_name": "content-generation-agent",
  "network_policy": {
    "internet_access": false,
    "allowed_domains": [
      "api.openai.com",
      "api.anthropic.com",
      "huggingface.co",
      "data.example.com"
    ],
    "allowed_ips": ["203.0.113.0/24"],
    "egress_rules": [],
    "current_k8s_policy": {
      "apiVersion": "networking.k8s.io/v1",
      "kind": "NetworkPolicy",
      "metadata": {
        "name": "content-generation-agent-network-policy"
      },
      "spec": {
        "podSelector": {
          "matchLabels": {
            "app": "content-generation-agent"
          }
        },
        "egress": [
          {
            "to": [
              {
                "dnsName": "api.openai.com"
              },
              {
                "dnsName": "api.anthropic.com"
              },
              {
                "dnsName": "huggingface.co"
              },
              {
                "dnsName": "data.example.com"
              }
            ]
          },
          {
            "to": [
              {
                "ipBlock": {
                  "cidr": "203.0.113.0/24"
                }
              }
            ]
          }
        ]
      }
    }
  }
}
```

</details>

## Request and Response Models

### AI Agent Runtime Models

```python
class AIAgentRuntimeRequest(BaseModel):
    name: str
    description: str = ""
    entrypoint: str
    code_source: CodeSource
    env_vars: Optional[List[EnvVar]] = None
    resources: Optional[ResourceRequirements] = None
    replicas: int = 1
    db_config: Optional[DBConfig] = None

class AIAgentRuntimeResponse(BaseModel):
    name: str
    namespace: str
    status: Optional[AIAgentRuntimeStatusResponse] = None
```

### Code Source Models

```python
class CodeSource(BaseModel):
    type: Literal["github", "configMap", "inline"]
    gitRepo: Optional[GitRepo] = None
    configMapName: Optional[str] = None

class GitRepo(BaseModel):
    url: str
    branch: str = "main"
    auth: Optional[GitRepoAuth] = None

class GitRepoAuth(BaseModel):
    type: Literal["token", "ssh"]
    token: Optional[str] = None
    sshKey: Optional[str] = None
```

### Environment Variable Models

```python
class EnvVar(BaseModel):
    name: str
    value: Optional[str] = None
    valueFrom: Optional[EnvVarSource] = None

class EnvVarSource(BaseModel):
    secretKeyRef: Optional[SecretKeySelector] = None
    configMapKeyRef: Optional[ConfigMapKeySelector] = None

class SecretKeySelector(BaseModel):
    name: str
    key: str

class ConfigMapKeySelector(BaseModel):
    name: str
    key: str
```

### Resource Requirement Models

```python
class ResourceRequirements(BaseModel):
    limits: Optional[Dict[str, str]] = None
    requests: Optional[Dict[str, str]] = None
```

### Token Models

```python
class TokenRequest(BaseModel):
    description: str
    duration: str = "24h"  # Format: "1h", "30d", etc.
    permissions: List[str] = ["read", "execute"]
    
class TokenResponse(BaseModel):
    token_id: str
    description: str
    access_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    created_at: datetime
    permissions: List[str]
    
class TokenMetadata(BaseModel):
    token_id: str
    description: str
    expires_at: datetime
    created_at: datetime
    created_by: str
    permissions: List[str]
    last_used: Optional[datetime] = None
```

### Network Policy Models

```python
class NetworkPolicy(BaseModel):
    internet_access: bool = True
    allowed_domains: List[str] = []
    allowed_ips: List[str] = []
    egress_rules: List[Dict[str, Any]] = []

class NetworkPolicyResponse(BaseModel):
    runtime_name: str
    network_policy: NetworkPolicy
    current_k8s_policy: Optional[Dict[str, Any]] = None
```

## Implementation Examples

### Basic Agent Deployment

<details>
<summary>Click to see deployment example</summary>

```python
import requests
import json

# Authentication
API_BASE_URL = "https://api.ai-agent-platform.example.com"
API_KEY = "your-api-key-here"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Define the runtime
runtime_data = {
    "name": "simple-agent",
    "description": "Simple CrewAI agent example",
    "entrypoint": "main.py",
    "code_source": {
        "type": "github",
        "gitRepo": {
            "url": "https://github.com/username/simple-crewai-agent",
            "branch": "main"
        }
    },
    "env_vars": [
        {
            "name": "OPENAI_API_KEY",
            "value": "sk-your-key-here"
        }
    ],
    "resources": {
        "requests": {
            "cpu": "100m",
            "memory": "256Mi"
        },
        "limits": {
            "cpu": "500m",
            "memory": "512Mi"
        }
    }
}

# Create the runtime
response = requests.post(f"{API_BASE_URL}/api/runtimes", 
                        headers=HEADERS, 
                        data=json.dumps(runtime_data))
print(f"Create response: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Get runtime status (poll until Running)
import time
runtime_name = runtime_data["name"]
max_attempts = 10
attempt = 0

while attempt < max_attempts:
    status_response = requests.get(f"{API_BASE_URL}/api/runtimes/{runtime_name}/status", 
                                  headers=HEADERS)
    status_data = status_response.json()
    print(f"Status: {status_data['status']['phase']}")
    
    if status_data['status']['phase'] == 'Running':
        print(f"Endpoint: {status_data['status']['endpoint']}")
        break
        
    attempt += 1
    time.sleep(5)
```

</details>

### File Upload Example

<details>
<summary>Click to see file upload example</summary>

```python
import requests

# Authentication
API_BASE_URL = "https://api.ai-agent-platform.example.com"
API_KEY = "your-api-key-here"
AUTH_HEADER = {"Authorization": f"Bearer {API_KEY}"}

# Runtime name
runtime_name = "file-upload-example"

# Create a simple runtime first with minimal configuration
runtime_data = {
    "name": runtime_name,
    "description": "Agent with file upload",
    "entrypoint": "main.py",
    "code_source": {
        "type": "inline"
    }
}

# Create the runtime
create_response = requests.post(
    f"{API_BASE_URL}/api/runtimes", 
    headers={**AUTH_HEADER, "Content-Type": "application/json"},
    json=runtime_data
)
print(f"Create response: {create_response.status_code}")

# Now upload the main file
with open("main.py", "rb") as f:
    files = {
        "file": ("main.py", f, "text/x-python")
    }
    data = {
        "filename": "main.py",
        "content_type": "text/x-python"
    }
    upload_response = requests.post(
        f"{API_BASE_URL}/api/runtimes/{runtime_name}/code/file",
        headers=AUTH_HEADER,
        files=files,
        data=data
    )
    print(f"Upload response: {upload_response.status_code}")
    print(upload_response.json())
```

</details>

### Runtime API Token Usage

<details>
<summary>Click to see runtime API token usage example</summary>

```python
import requests
import json
import time
from datetime import datetime, timedelta

# Authentication for Management API
API_BASE_URL = "https://api.ai-agent-platform.example.com"
MGMT_API_KEY = "your-management-api-key-here"
MGMT_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MGMT_API_KEY}"
}

# Get runtime details
runtime_name = "content-generation-agent"
runtime_response = requests.get(
    f"{API_BASE_URL}/api/runtimes/{runtime_name}",
    headers=MGMT_HEADERS
)
runtime_data = runtime_response.json()
runtime_url = runtime_data["status"]["endpoint"]

# Request a token for the runtime
token_response = requests.post(
    f"{API_BASE_URL}/api/runtimes/{runtime_name}/tokens",
    headers=MGMT_HEADERS,
    json={
        "description": "API client access",
        "duration": "24h",
        "permissions": ["read", "execute"]
    }
)
token_data = token_response.json()
runtime_token = token_data["access_token"]

# Use the token to interact with the Runtime API
runtime_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {runtime_token}"
}

# Submit a job to the runtime
job_response = requests.post(
    f"{runtime_url}/kickoff",
    headers=runtime_headers,
    json={
        "crew": "ContentCreationCrew",
        "inputs": {
            "topic": "AI Agent Architecture"
        }
    }
)
job_data = job_response.json()
job_id = job_data["job_id"]

# Poll for job completion
max_attempts = 20
attempt = 0
job_completed = False

while attempt < max_attempts and not job_completed:
    job_status_response = requests.get(
        f"{runtime_url}/job/{job_id}",
        headers=runtime_headers
    )
    job_status_data = job_status_response.json()
    
    if job_status_data["status"] in ["completed", "error"]:
        job_completed = True
        print(f"Job completed with status: {job_status_data['status']}")
        if "result" in job_status_data:
            print(f"Content length: {job_status_data['result']['length']}")
    else:
        print(f"Job status: {job_status_data['status']}")
        attempt += 1
        time.sleep(5)

# When finished with the token, revoke it
requests.delete(
    f"{API_BASE_URL}/api/runtimes/{runtime_name}/tokens/{token_data['token_id']}",
    headers=MGMT_HEADERS
)
```

</details>

## Environment Configuration

The Management API requires certain environment variables for proper operation:

### Database Configuration

```bash
# PostgreSQL database configuration
DATABASE_URL=postgresql://username:password@db.example.com:5432/ai_platform_db
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10
```

### Kubernetes Configuration

```bash
# Kubernetes configuration
# For in-cluster deployment, these can be left empty
# For external access, provide kubeconfig or credentials
K8S_NAMESPACE=ai-platform
AGENT_IMAGE=ai-platform/agent-runtime:latest
```

### Security Configuration

```bash
# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Troubleshooting

> [!WARNING]
> Common issues you might encounter when using the Management API and how to solve them.

<details>
<summary>Authentication Issues</summary>

**Problem**: Getting 401 Unauthorized errors

**Solutions**:

- Check that your API key is valid and not expired
- Ensure the Authorization header is formatted correctly (`Bearer your-token-here`)
- Verify that your JWT token hasn't expired

</details>

<details>
<summary>Deployment Issues</summary>

**Problem**: Runtime doesn't reach Running state

**Solutions**:

- Check runtime logs for specific errors: `GET /api/runtimes/{name}/logs`
- Verify that your code source is accessible
- Ensure your entrypoint file exists in the repository
- Check resource allocation (may be too low)
- Verify environment variables are set correctly

</details>

<details>
<summary>Code Source Issues</summary>

**Problem**: GitHub repository connection failures

**Solutions**:

- For private repositories, ensure your token has correct permissions
- Verify the repository URL and branch name
- Check if SSH key is formatted correctly for SSH authentication
- Ensure the repository actually contains your agent code

</details>

<details>
<summary>Token Issues</summary>

**Problem**: Getting 401 Unauthorized when accessing Runtime API

**Solutions**:

- Verify that the token hasn't expired
- Check that the token was issued for the correct runtime
- Ensure the token has the necessary permissions
- Try requesting a new token from the Management API
- Confirm that the runtime is in the "Running" state

</details>

<details>
<summary>Network Policy Issues</summary>

**Problem**: Runtime cannot access external services

**Solutions**:
- Check the network policy configuration for the runtime
- Verify the allowed domains list includes all required service domains
- Ensure proper DNS resolution is working within the cluster
- For advanced configurations, examine the Kubernetes NetworkPolicy objects directly
- If using `allowed_ips`, verify the CIDR notation is correct

</details>

## Security Best Practices

When using the Management API, follow these security best practices:

1. **API Keys**:
   - Rotate your API keys regularly
   - Never commit API keys to source control
   - Use environment variables for storing API keys

2. **Environment Variables**:
   - Use secrets for sensitive environment variables
   - Encrypt sensitive data before storing
   - Implement least privilege access to secrets

3. **Network Security**:
   - Use HTTPS for all API requests
   - Implement IP allowlisting if possible
   - Monitor for suspicious API usage patterns

4. **Code Security**:
   - Validate code before deployment
   - Scan for security vulnerabilities
   - Use secure coding practices

### Runtime API Token Security

1. **Token Management**:
   - Request tokens with the minimum permissions and duration needed
   - Revoke tokens when they are no longer needed
   - Never share tokens between different clients or services
   - Store tokens securely (environment variables, secret managers)

2. **Integration Security**:
   - Create dedicated tokens for each integration or service
   - Use shorter expiration times for higher-risk scenarios
   - Implement token refresh logic for long-running processes
   - Audit token usage regularly

3. **Troubleshooting**:
   - Don't log full tokens, only truncated versions for diagnostics
   - Rotate tokens if a security incident is suspected
   - Monitor for unusual token usage patterns
   - If leakage is suspected, revoke tokens immediately
