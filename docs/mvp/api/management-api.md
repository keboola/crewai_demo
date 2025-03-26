# Management API

The Management API is a RESTful API that allows you to create, read, update, and delete AI Agent Runtimes. The API is implemented using FastAPI and follows RESTful principles.

## Base URL

The base URL for the Management API is `/api`.

## Endpoints

### Runtimes

#### Create a Runtime

##### From Git Repository

**POST** `/api/runtimes`

Creates a new AI Agent Runtime based on code from a Git repository.

**Request Body (JSON)**:
```json
{
  "name": "my-agent-runtime",
  "namespace": "default",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/example/agent-repo.git",
      "branch": "main"
    }
  }
}
```

If using a private Git repository with Personal Access Token (PAT) authentication:

```json
{
  "name": "my-private-agent-runtime",
  "namespace": "default", 
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/example/private-agent-repo.git",
      "branch": "main",
      "auth": {
        "type": "pat",
        "token": "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
      }
    }
  }
}
```

**Note**: Both snake_case (`git_repo`) and camelCase (`gitRepo`) field names are supported.

**Response**: 
```json
{
  "name": "my-agent-runtime",
  "namespace": "default",
  "status": "Creating",
  "created_at": "2023-04-22T10:30:00Z",
  "id": "12345678-abcd-1234-efgh-123456789abc"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8080/api/runtimes" \
  -H "Content-Type: application/json" \
  -d @runtime_config_git.json
```

##### From File Upload

**POST** `/api/runtimes/from-file`

Creates a new AI Agent Runtime based on an uploaded code file.

**Request Body (multipart/form-data)**:
- `file`: The Python file containing the agent code
- `runtime_config`: A JSON string containing the runtime configuration

Example runtime_config:
```json
{
  "name": "my-file-agent-runtime",
  "namespace": "default",
  "codeSource": {
    "type": "file"
  }
}
```

**Response**: 
```json
{
  "name": "my-file-agent-runtime",
  "namespace": "default",
  "status": "Creating",
  "created_at": "2023-04-22T10:30:00Z",
  "id": "12345678-abcd-1234-efgh-123456789abc"
}
```

**Example with JSON string in form field**:
```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -F "file=@my_agent.py" \
  -F "runtime_config={\"name\":\"my-file-agent-runtime\",\"namespace\":\"default\",\"codeSource\":{\"type\":\"file\"}}"
```

**Example with JSON file**:
```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -F "file=@my_agent.py" \
  -F "runtime_config_file=@runtime_config_file.json"
```

This endpoint is designed specifically for file uploads and provides a simpler interface when working with file-based deployments than the main `/api/runtimes` endpoint.

#### List all Runtimes

**GET** `/api/runtimes`

Returns a list of all AI Agent Runtimes.

**Query Parameters**:
- `namespace` (optional): Filter runtimes by namespace

**Response**:
```json
[
  {
    "name": "my-agent-runtime",
    "namespace": "default",
    "status": "Running",
    "created_at": "2023-04-22T10:30:00Z",
    "id": "12345678-abcd-1234-efgh-123456789abc"
  },
  {
    "name": "another-agent-runtime",
    "namespace": "default",
    "status": "Creating",
    "created_at": "2023-04-22T11:15:00Z",
    "id": "87654321-dcba-4321-hgfe-cba987654321"
  }
]
```

#### Get a Runtime

**GET** `/api/runtimes/{name}`

Returns details about a specific AI Agent Runtime.

**Path Parameters**:
- `name`: The name of the runtime

**Query Parameters**:
- `namespace` (optional): The namespace of the runtime, defaults to "default"

**Response**:
```json
{
  "name": "my-agent-runtime",
  "namespace": "default",
  "status": "Running",
  "created_at": "2023-04-22T10:30:00Z",
  "url": "http://my-agent-runtime.default.svc.cluster.local:8080",
  "id": "12345678-abcd-1234-efgh-123456789abc",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/example/agent-repo.git",
      "branch": "main"
    }
  }
}
```

#### Delete a Runtime

**DELETE** `/api/runtimes/{name}`

Deletes a specific AI Agent Runtime.

**Path Parameters**:
- `name`: The name of the runtime

**Query Parameters**:
- `namespace` (optional): The namespace of the runtime, defaults to "default"

**Response**: `204 No Content`

## Error Responses

The API returns standard HTTP status codes to indicate success or failure:

- `200 OK`: The request was successful
- `201 Created`: A new resource was created
- `204 No Content`: The request was successful but there is no content to return
- `400 Bad Request`: The request was invalid
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An internal server error occurred

Error responses include a JSON body with details about the error:

```json
{
  "detail": "Error message"
}
```

## Code Source Types

The Management API supports the following code source types:

### Git Repository (`git`)

Used for deploying agents from Git repositories, with optional authentication.

```json
{
  "type": "git",
  "gitRepo": {
    "url": "https://github.com/example/agent-repo.git",
    "branch": "main"
  }
}
```

With authentication:

```json
{
  "type": "git",
  "gitRepo": {
    "url": "https://github.com/example/private-agent-repo.git",
    "branch": "main",
    "auth": {
      "type": "pat",
      "token": "ghp_abcdefghijklmnopqrstuvwxyz0123456789"
    }
  }
}
```

### File Upload (`file`)

Used for deploying agents from files uploaded through the Management API.

```json
{
  "type": "file"
}
```

When using this type, you must upload the file using the `/api/runtimes/from-file` endpoint.

# AI Agent Platform Management API

> [!NOTE]
> This documentation explains how to use the Management API to deploy and manage AI Agent Runtimes on the AI Agent Platform.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [AI Agent Runtimes](#ai-agent-runtimes)
  - [Environment Variables](#environment-variables)
  - [Runtime Operations](#runtime-operations)
- [Request and Response Models](#request-and-response-models)
- [Implementation Examples](#implementation-examples)
- [Environment Configuration](#environment-configuration)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Further Resources](#further-resources)

## Overview

The AI Agent Platform Management API provides a user-friendly interface for creating and managing AI Agent Runtimes. It translates your requests into Kubernetes resources that run your CrewAI agents and exposes them as web services.

Key features:

- **Simple Deployment**: Deploy CrewAI agents with minimal configuration
- **Code Management**: Upload code directly or integrate with GitHub repositories
- **Environment Management**: Configure environment variables for your agents
- **Scalability**: Control resource allocation and replica count
- **Operations**: Restart, monitor, and manage your deployed agents

## Quick Start

To deploy your first agent using the Management API:

1. **Set up authentication**:

   ```bash
   # Save your API token to an environment variable
   export API_AUTH_TOKEN="your-auth-token-here"
   ```

2. **Deploy your first agent**:

   ```bash
   curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
     -d '{
       "name": "my-first-agent",
       "description": "My first CrewAI agent",
       "entrypoint": "crewai_app/orchestrator.py",
       "codeSource": {
         "type": "git",
         "gitRepo": {
           "url": "https://github.com/username/my-crewai-project",
           "branch": "main"
         }
       },
       "envVars": [
         {
           "name": "OPENAI_API_KEY",
           "value": "sk-...",
           "secure": true
         }
       ]
     }'
   ```

3. **Check deployment status**:

   ```bash
   curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/my-first-agent" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}"
   ```

4. **Access your deployed agent**:

   When using ingress, your agent will be available at:

   ```
   https://my-first-agent.agentic.canary-orion.keboola.dev
   ```

   For local development without ingress, use port-forwarding:

   ```bash
   kubectl port-forward svc/my-first-agent 8000:80
   ```

   Then access your agent at `http://localhost:8000`

## Authentication

The Management API uses token-based authentication. Include an Authorization header with a Bearer token in all requests:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

The API token is configured through the environment variable `API_AUTH_TOKEN`. Authentication can be disabled (not recommended for production) by setting `API_AUTH_ENABLED=false` in your environment.

## API Endpoints

### AI Agent Runtimes

#### Create a New Runtime

**Endpoint**: `POST /api/runtimes`

Creates a new AI Agent Runtime deployment.

**Request Parameters**:

- `namespace` (optional): Kubernetes namespace (can be provided in request body)
- `dry_run` (optional): If true, only returns the manifest without creating it (default: false)

**Request Body**:

```json
{
  "name": "my-agent",
  "description": "My CrewAI agent",
  "entrypoint": "crewai_app/main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/my-crewai-project",
      "branch": "main"
    }
  },
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-...",
      "secure": true
    }
  ],
  "replicas": 1,
  "resources": {
    "limits": {
      "cpu": "1",
      "memory": "1Gi"
    },
    "requests": {
      "cpu": "500m",
      "memory": "512Mi"
    }
  }
}
```

**Example**:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "name": "content-agent",
    "description": "Content generation agent",
    "entrypoint": "crewai_app/main.py",
    "codeSource": {
      "type": "git",
      "gitRepo": {
        "url": "https://github.com/username/content-agent",
        "branch": "main"
      }
    },
    "envVars": [
      {
        "name": "OPENAI_API_KEY",
        "value": "sk-...",
        "secure": true
      }
    ]
  }'
```

**Response**:

```json
{
  "name": "content-agent",
  "namespace": "default",
  "status": {
    "phase": "Running",
    "message": "Runtime is running",
    "last_transition_time": "2023-06-15T12:34:56Z",
    "pod_status": "Running",
    "service_status": "Active"
  },
  "spec": {
    "name": "content-agent",
    "description": "Content generation agent",
    "entrypoint": "crewai_app/main.py",
    "code_source": {
      "type": "git",
      "git_repo": {
        "url": "https://github.com/username/content-agent",
        "branch": "main"
      }
    },
    "replicas": 1
  }
}
```

#### List All Runtimes

**Endpoint**: `GET /api/runtimes`

Lists all AI Agent Runtimes in the Management API's namespace.

**Example**:

```bash
# List all runtimes
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

**Response**:

```json
[
  {
    "name": "content-agent",
    "namespace": "default",
    "url": "https://content-agent.agentic.canary-orion.keboola.dev",
    "status": {
      "phase": "Running",
      "message": "Runtime is running",
      "last_transition_time": "2023-06-15T12:34:56Z",
      "pod_status": "Running",
      "service_status": "Active"
    },
    "spec": {
      "name": "content-agent",
      "description": "Content generation agent",
      "entrypoint": "crewai_app/main.py",
      "code_source": {
        "type": "git",
        "git_repo": {
          "url": "https://github.com/username/content-agent",
          "branch": "main"
        }
      },
      "replicas": 1
    }
  }
]
```

#### Get Runtime Details

**Endpoint**: `GET /api/runtimes/{name}`

Gets details of a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Example**:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/content-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

**Response**:

```json
{
  "name": "content-agent",
  "namespace": "default",
  "url": "https://content-agent.agentic.canary-orion.keboola.dev",
  "status": {
    "phase": "Running",
    "message": "Runtime is running",
    "last_transition_time": "2023-06-15T12:34:56Z",
    "pod_status": "Running",
    "service_status": "Active"
  },
  "spec": {
    "name": "content-agent",
    "description": "Content generation agent",
    "entrypoint": "crewai_app/main.py",
    "code_source": {
      "type": "git",
      "git_repo": {
        "url": "https://github.com/username/content-agent",
        "branch": "main"
      }
    },
    "env_vars": [
      {
        "name": "OPENAI_API_KEY",
        "secure": true
      },
      {
        "name": "LOG_LEVEL",
        "value": "INFO",
        "secure": false
      }
    ],
    "replicas": 1,
    "resources": {
      "limits": {
        "cpu": "1",
        "memory": "1Gi"
      },
      "requests": {
        "cpu": "500m",
        "memory": "512Mi"
      }
    }
  }
}
```

#### Delete Runtime

**Endpoint**: `DELETE /api/runtimes/{name}`

Deletes a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Example**:

```bash
curl -X DELETE "https://agentic.canary-orion.keboola.dev/api/runtimes/content-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

**Response**:

No content (204)

#### Restart Runtime

**Endpoint**: `POST /api/runtimes/{name}/restart`

Restarts a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Example**:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/content-agent/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

**Response**:

```json
{
  "name": "content-agent",
  "namespace": "default",
  "url": "https://content-agent.agentic.canary-orion.keboola.dev",
  "status": {
    "phase": "Restarting",
    "message": "Runtime is restarting",
    "last_transition_time": "2023-06-15T14:22:33Z",
    "pod_status": "Terminating",
    "service_status": "Active"
  },
  "spec": {
    "name": "content-agent",
    "description": "Content generation agent",
    "entrypoint": "crewai_app/main.py",
    "code_source": {
      "type": "git",
      "git_repo": {
        "url": "https://github.com/username/content-agent",
        "branch": "main"
      }
    },
    "replicas": 1
  }
}
```

#### Create Runtime from Git Repository

**Endpoint**: `POST /api/runtimes`

Creates a new AI Agent Runtime with a Git repository as the code source.

**Request Body**:

```json
{
  "name": "content-agent",
  "description": "Content generation agent",
  "entrypoint": "crewai_app/main.py",
  "code_source": {
    "type": "git",
    "git_repo": {
      "url": "https://github.com/username/content-agent",
      "branch": "main"
    }
  },
  "replicas": 1
}
```

#### Create Runtime with File Upload

**Endpoint**: `POST /api/runtimes/from-file`

Creates a new AI Agent Runtime based on an uploaded code file.

**Request Body (multipart/form-data)**:
- `file`: The Python file containing the agent code
- `runtime_config`: A JSON string containing the runtime configuration

Example runtime_config:
```json
{
  "name": "content-creation-agent-file-upload",
  "description": "Content Creation Agent using CrewAI (File Upload)",
  "entrypoint": "orchestrator_with_numpy.py",
  "codeSource": {
    "type": "file"
  },
  "replicas": 1,
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-or-v1-hey",
      "secure": true
    },
    {
      "name": "OPENAI_API_BASE",
      "value": "https://openrouter.ai/api/v1",
      "secure": true
    },
    {
      "name": "OPENROUTER_MODEL",
      "value": "openai/gpt-4o-mini",
      "secure": true
    },
    {
      "name": "STORAGE_TYPE",
      "value": "memory",
      "secure": false
    },
    {
      "name": "DEBUG",
      "value": "true",
      "secure": false
    }
  ]
}
```

**Response**: 
```json
{
  "name": "content-creation-agent-file-upload",
  "namespace": "default",
  "status": "Creating",
  "created_at": "2023-04-22T10:30:00Z",
  "id": "12345678-abcd-1234-efgh-123456789abc"
}
```

**Example with JSON string in form field**:
```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -F "file=@my_agent.py" \
  -F "runtime_config={\"name\":\"my-file-agent-runtime\",\"namespace\":\"default\",\"codeSource\":{\"type\":\"file\"}}"
```

**Example with JSON file**:
```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -F "file=@my_agent.py" \
  -F "runtime_config_file=@runtime_config_file.json"
```

This endpoint is designed specifically for file uploads and provides a simpler interface when working with file-based deployments than the main `/api/runtimes` endpoint.

### Environment Variables

Environment variables can be configured when creating or updating a runtime:

```json
{
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-...",
      "secure": true
    },
    {
      "name": "DEBUG",
      "value": "true",
      "secure": false
    }
  ]
}
```

The `secure` flag (default: `false`) determines how the variable is stored:
- When `secure: true`, the value is stored securely and not exposed in logs or API responses
- When `secure: false` (default), the value is stored as a regular environment variable

All environment variables, regardless of their `secure` setting, are mounted as environment variables in the runtime container.

### Runtime Operations

The following operations are available for managing AI Agent Runtimes:

#### Restart Runtime

Restart a runtime to apply configuration changes or recover from errors:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/my-agent/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Delete Runtime

Remove a runtime and all associated resources:

```bash
curl -X DELETE "https://agentic.canary-orion.keboola.dev/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Get Runtime Status

Check the current status of a runtime:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

## Request and Response Models

### Runtime Creation Model

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Name of the AI Agent Runtime (must be DNS-compliant) | Yes |
| `description` | string | Description of the AI Agent Runtime | No |
| `entrypoint` | string | Path to the entry Python file | Yes |
| `codeSource` | object | Configuration for the source of the code | Yes |
| `envVars` | array | Environment variables for the AI agent | No |
| `resources` | object | CPU and memory resource requirements | No |
| `replicas` | integer | Number of replicas (default: 1) | No |

### Code Source Models

#### Git Repository Source

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | string | Must be "git" | Yes |
| `gitRepo.url` | string | URL of the Git repository | Yes |
| `gitRepo.branch` | string | Branch to checkout (default: "main") | No |
| `gitRepo.auth` | object | Authentication configuration | No |

#### Inline Source (File Upload)

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | string | Must be "inline" | Yes |

## Implementation Examples

See the [API Examples](./examples/management-api-curl.md) page for detailed examples of:

- Creating a simple runtime with Git repository
- Creating a runtime with file upload
- Working with environment variables
- Advanced configuration options

## Environment Configuration

The Management API can be configured using environment variables:

### API Authentication

- `API_AUTH_ENABLED`: Enable/disable API authentication (default: `true`)
- `API_AUTH_TOKEN`: The authentication token for API requests

### Server Configuration

- `API_HOST`: Host to bind the server to (default: `0.0.0.0`)
- `API_PORT`: Port to listen on (default: `8080`)
- `API_DEBUG`: Enable debug mode (default: `false`)
