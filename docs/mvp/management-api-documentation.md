# AI Agent Platform Management API

> [!NOTE]
> This documentation outlines the Management API for the AI Agent Platform, which allows AI engineers to deploy and manage CrewAI agents on Kubernetes.

## Table of Contents

- [Overview](#overview)
- [Current Implementation Status](#current-implementation-status)
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

The AI Agent Platform Management API provides a user-friendly interface for creating and managing AI Agent Runtimes. It translates your requests into Kubernetes resources that run your CrewAI agents and exposes them as web services.

Key features:

- **Simple Deployment**: Deploy CrewAI agents with minimal configuration
- **Code Management**: Upload code directly or integrate with GitHub repositories
- **Environment Management**: Configure environment variables for your agents
- **Scalability**: Control resource allocation and replica count
- **Operations**: Restart, monitor, and manage your deployed agents

## Current Implementation Status

> [!IMPORTANT]
> This documentation represents the current implementation of the Management API. Below is a summary of the implemented features.

### Implemented Features

✅ **Core API Structure**

- FastAPI application framework
- Pydantic v2 models for request/response validation
- Kubernetes service layer
- Token-based authentication with `API_AUTH_TOKEN`

✅ **Runtime Management Endpoints**

- Create runtime with Git repository source
- List all runtimes
- Get runtime details
- Delete runtime
- Restart runtime
- File upload deployment via `/api/runtimes/from-file`

✅ **Environment Variable Support**

- Environment variables in runtime creation
- Support for both plain and secure variables
- Namespace configuration via query params or request body

✅ **Code Source Management**

- Git repository integration
- File upload support
- Code source configuration

### Authentication

The Management API uses token-based authentication. All requests must include an Authorization header with a Bearer token:

```bash
curl -X GET "http://localhost:8080/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

### Configuration

The API token is configured through the environment variable `API_AUTH_TOKEN`. You can:

1. Set it directly in your environment:

   ```bash
   export API_AUTH_TOKEN="your-auth-token-here"
   ```

2. Include it in your .env file:

   ```bash
   API_AUTH_TOKEN=your-auth-token-here
   ```

3. Pass it as an environment variable when running containers:

   ```bash
   docker run -e API_AUTH_TOKEN=your-auth-token-here ...
   ```

Authentication can be disabled by setting `API_AUTH_ENABLED=false` in your environment.

### Examples

**Creating a runtime with authentication:**

```bash
# First set your token
export API_AUTH_TOKEN="your-auth-token-here"

# Then use it in your API requests
curl -X POST "http://localhost:8080/api/runtimes" \
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
        "value": "sk-..."
      }
    ]
  }'
```

**File upload with authentication:**

```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

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

   When using ingress (with RUNTIME_INGRESS_DOMAIN configured), your agent will be available at:

   ```
   https://my-first-agent.agentic.canary-orion.keboola.dev
   ```

   For local development without ingress, use port-forwarding:

   ```bash
   kubectl port-forward svc/my-first-agent 8000:80
   ```

   Then access your agent at `http://localhost:8000`

   For local development WITH ingress support, you can use Traefik with nip.io or traefik.me:

   ```bash
   # Configure RUNTIME_INGRESS_DOMAIN using your local IP with nip.io
   export RUNTIME_INGRESS_DOMAIN="192.168.1.100.nip.io"
   
   # Or use traefik.me which automatically resolves to 127.0.0.1
   export RUNTIME_INGRESS_DOMAIN="traefik.me"
   ```

   Then access your agent at `http://my-first-agent.traefik.me` or `http://my-first-agent.192.168.1.100.nip.io`

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
  },
  "dbConfig": {
    "type": "sqlite"
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

Note: The `url` field will only be present in the response if `RUNTIME_INGRESS_DOMAIN` is configured. Otherwise, you can access the runtime using port-forwarding.

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
  },
  {
    "name": "research-agent",
    "namespace": "default",
    "url": "https://research-agent.agentic.canary-orion.keboola.dev",
    "status": {
      "phase": "Running",
      "message": "Runtime is running",
      "last_transition_time": "2023-06-14T10:22:45Z",
      "pod_status": "Running",
      "service_status": "Active"
    },
    "spec": {
      "name": "research-agent",
      "description": "Research assistant agent",
      "entrypoint": "app.py",
      "code_source": {
        "type": "git",
        "git_repo": {
          "url": "https://github.com/username/research-agent",
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

Gets details of a specific AI Agent Runtime in the Management API's namespace.

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

Deletes a specific AI Agent Runtime in the Management API's namespace.

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

Restarts a specific AI Agent Runtime in the Management API's namespace.

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

#### Create Runtime from File

**Endpoint**: `POST /api/runtimes/from-file`

Creates a new AI Agent Runtime using an uploaded code file (ZIP archive) and a runtime configuration.

**Request Parameters**:

This endpoint accepts runtime configuration in three different formats:

1. **As a form field (string)**:
   - `runtime_config` (form field): JSON string containing the runtime configuration
   - `file` (form file): ZIP archive containing the code files for the agent
   
   ```bash
   curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/from-file" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
     -F "runtime_config=$(cat runtime_config.json)" \
     -F "file=@agent_code.zip"
   ```

2. **As a separate file upload**:
   - `runtime_config_file` (form file): JSON file containing the runtime configuration
   - `file` (form file): ZIP archive containing the code files for the agent
   
   ```bash
   curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/from-file" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
     -F "runtime_config_file=@runtime_config.json" \
     -F "file=@agent_code.zip"
   ```

3. **As direct JSON in the request body**:
   - Body JSON: Runtime configuration as direct JSON in the request body
   - `file` (form file): ZIP archive containing the code files for the agent
   
   ```bash
   curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/from-file" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@agent_code.zip" \
     --data-raw '{
       "name": "file-upload-runtime",
       "description": "Runtime created from file upload",
       "entrypoint": "main.py",
       "codeSource": {"type": "inline"},
       "envVars": [{"name": "OPENAI_API_KEY", "value": "sk-...", "secure": true}],
       "replicas": 1
     }'
   ```

**Example Runtime Configuration**:

```json
{
  "name": "file-upload-agent",
  "description": "Agent using file upload",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "inline"
  },
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-...",
      "secure": true
    },
    {
      "name": "DEBUG",
      "value": "true"
    }
  ],
  "replicas": 1
}
```

**Response**:

```json
{
  "name": "file-upload-agent",
  "status": "creating",
  "message": "AI Agent Runtime created successfully from file upload"
}
```

Note: If `RUNTIME_INGRESS_DOMAIN` is configured, the response will also include a `url` field with the full URL to access the runtime.

### Environment Variables

Environment variables can be configured when creating or updating a runtime in two ways:

1. Direct values in the runtime creation request
2. References to Kubernetes secrets or configmaps

#### Direct Environment Variables

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
      "value": "true"
    }
  ]
}
```

The `secure` flag (default: `false`) stores the variable in a Kubernetes Secret instead of directly in the deployment.

#### Using Kubernetes Secrets and ConfigMaps

For sensitive data, reference existing Kubernetes secrets:

```json
{
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "valueFrom": {
        "secretKeyRef": {
          "name": "api-keys",
          "key": "openai"
        }
      }
    }
  ]
}
```

Or use ConfigMaps for non-sensitive configuration:

```json
{
  "envVars": [
    {
      "name": "LOG_LEVEL",
      "valueFrom": {
        "configMapKeyRef": {
          "name": "app-config",
          "key": "log-level"
        }
      }
    }
  ]
}
```

### Code Management

Code for AI Agent Runtimes can be sourced in several ways:

#### Git Repository

Use a Git repository as the code source:

```json
{
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/my-agent",
      "branch": "main"
    }
  }
}
```

For private repositories, include authentication:

```json
{
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/my-agent",
      "branch": "main",
      "auth": {
        "type": "token",
        "token": "github_pat_..."
      }
    }
  }
}
```

#### File Upload

Upload code directly using the `/api/runtimes/from-file` endpoint as shown [earlier](#create-runtime-from-file).

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
| `dbConfig` | object | Database configuration for the agent | No |

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

### Creating a Simple Runtime

```bash
# Create runtime configuration
cat > runtime_config.json << EOF
{
  "name": "hello-agent",
  "description": "Simple hello world agent",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/hello-agent",
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
EOF

# Create the runtime
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d @runtime_config.json
```

### File Upload Deployment

```bash
# Create a simple agent
mkdir my-agent
cat > my-agent/main.py << EOF
import os
from openai import OpenAI

def main():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
EOF

cat > my-agent/requirements.txt << EOF
openai==1.12.0
EOF

# Create runtime configuration
cat > runtime_config.json << EOF
{
  "name": "file-agent",
  "description": "Agent deployed via file upload",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "inline"
  },
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-...",
      "secure": true
    }
  ]
}
EOF

# Zip the agent code
zip -r agent_code.zip my-agent/

# Upload code and configuration
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

## Environment Configuration

The Management API can be configured using environment variables:

### API Authentication

- `API_AUTH_ENABLED`: Enable/disable API authentication (default: `true`)
- `API_AUTH_TOKEN`: The authentication token for API requests

### Server Configuration

- `API_HOST`: Host to bind the server to (default: `0.0.0.0`)
- `API_PORT`: Port to listen on (default: `8080`)
- `API_DEBUG`: Enable debug mode (default: `false`)

### Kubernetes Configuration

- `DEFAULT_NAMESPACE`: Namespace where the Management API operates and deploys runtimes (default: `default`)
- `RUNTIME_INGRESS_DOMAIN`: Domain for runtime URLs (optional, only needed when using ingress)
- `KUBERNETES_CONFIG_PATH`: Path to kubeconfig file (optional)
- `KUBERNETES_CONTEXT`: Kubernetes context to use (optional)

### Local Development with Ingress

For local development, you can simulate a production-like environment with ingress using Traefik and wildcard DNS services. This gives you a more realistic testing environment without needing to set up complex DNS.

#### Option 1: Using nip.io

[nip.io](https://nip.io/) is a free wildcard DNS service that maps any IP address to a hostname. Format: `<anything>.<IP>.nip.io` resolves to `<IP>`.

1. Install Traefik in your Kubernetes cluster using Helm:

   ```bash
   helm repo add traefik https://helm.traefik.io/traefik
   helm install traefik traefik/traefik --set ports.web.exposedPort=80 --set ports.websecure.exposedPort=443
   ```

2. Configure the Management API with your local IP address:

   ```bash
   export RUNTIME_INGRESS_DOMAIN="192.168.1.100.nip.io"  # Replace with your actual IP
   ```

3. Create and access your runtimes:

   ```bash
   # Your runtime will be available at:
   http://my-runtime.192.168.1.100.nip.io
   ```

#### Option 2: Using traefik.me

[traefik.me](https://traefik.me/) is another wildcard DNS service specifically designed for Traefik users. Format: `<anything>.traefik.me` resolves to `127.0.0.1`.

1. Install Traefik as above.

2. Configure the Management API:

   ```bash
   export RUNTIME_INGRESS_DOMAIN="traefik.me"
   ```

3. Create and access your runtimes:

   ```bash
   # Your runtime will be available at:
   http://my-runtime.traefik.me
   ```

Benefits of this approach:

- No need to modify `/etc/hosts` files
- Works with any number of subdomains
- Enables testing of multi-runtime setups
- Closely mimics production environment with real domain names
- Supports testing from other devices on your network (with nip.io)
- traefik.me even provides wildcard SSL certificates for HTTPS testing

### Resource Defaults

- `DEFAULT_CPU_REQUEST`: Default CPU request for runtimes (default: `100m`)
- `DEFAULT_MEMORY_REQUEST`: Default memory request for runtimes (default: `256Mi`)
- `DEFAULT_CPU_LIMIT`: Default CPU limit for runtimes (default: `500m`)
- `DEFAULT_MEMORY_LIMIT`: Default memory limit for runtimes (default: `512Mi`)

## Troubleshooting

### Common Errors

1. **Authentication Errors**

   ```bash
   # Missing token
   curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes"
   # Response: {"detail":"Not authenticated"}

   # Invalid token
   curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes" \
     -H "Authorization: Bearer invalid-token"
   # Response: {"detail":"Invalid authentication credentials"}
   ```

2. **Resource Not Found**

   ```bash
   curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/non-existent" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}"
   # Response: {"detail":"AI Agent Runtime not found: non-existent"}
   ```

3. **Invalid Configuration**

   ```bash
   curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
     -d '{
       "name": "invalid-agent",
       "codeSource": {
         "type": "unknown"
       }
     }'
   # Response: {"detail":"Invalid code source type: unknown"}
   ```

### Troubleshooting Tips

1. **Check logs**:
   - Look at the management API logs for detailed error information
   - Check Kubernetes logs if the runtime is stuck in a pending state

2. **Resource availability**:
   - Ensure your cluster has enough resources for the requested CPU/memory
   - Verify that storage is available for your deployments

3. **Network issues**:
   - If the runtime URL is not accessible, check network policies
   - Verify that your DNS and ingress configurations are correct

## Security Best Practices

1. **API Authentication**
   - Always enable authentication in production
   - Use strong, randomly generated tokens
   - Rotate tokens periodically
   - Store tokens securely

2. **Environment Variables**
   - Use `secure: true` for all sensitive data
   - Do not commit API keys or secrets to source code repositories
   - Consider using external secret management solutions

3. **Resource Limits**
   - Always set appropriate resource limits to prevent DoS
   - Monitor resource usage regularly
   - Start with conservative limits and increase as needed

4. **Code Security**
   - Validate all input files before uploading
   - Use trusted repositories for code sources
   - Regularly check for and update dependencies with security issues

## Further Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/): Learn more about FastAPI, the framework used to build the Management API
- [Kubernetes Documentation](https://kubernetes.io/docs/): Official Kubernetes documentation for understanding container orchestration
- [OpenAPI Specification](https://swagger.io/specification/): API specification standard used by the Management API

### Tools and Utilities

- [kubectl](https://kubernetes.io/docs/reference/kubectl/): Command-line tool for interacting with Kubernetes clusters
- [curl](https://curl.se/docs/): Command-line tool for making HTTP requests
- [jq](https://stedolan.github.io/jq/): Command-line JSON processor for formatting API responses

### Development Resources

- [Python Package Index (PyPI)](https://pypi.org/): Find Python packages and dependencies
- [Docker Documentation](https://docs.docker.com/): Learn about containerization and Docker
- [Git Documentation](https://git-scm.com/doc): Version control system documentation

### Security Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/): Best practices for API security
- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/): Security concepts in Kubernetes
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/): Security features in FastAPI

### Community and Support

- [GitHub Repository](https://github.com/username/ai-agent-platform): Source code and issue tracking
- [Stack Overflow](https://stackoverflow.com/questions/tagged/fastapi): Community Q&A for FastAPI
- [Kubernetes Slack](https://kubernetes.slack.com/): Community chat for Kubernetes

### Related Projects

- [Helm](https://helm.sh/): Package manager for Kubernetes
- [Prometheus](https://prometheus.io/): Monitoring and alerting toolkit
- [Grafana](https://grafana.com/): Analytics and monitoring solution

### Best Practices

- [The Twelve-Factor App](https://12factor.net/): Methodology for building modern applications
- [API Design Guide](https://cloud.google.com/apis/design): Google's API design guide
- [Kubernetes Patterns](https://k8spatterns.io/): Common patterns for Kubernetes applications

### Tutorials and Guides

1. **Getting Started**
   - [Quick Start Guide](docs/quickstart.md)
   - [Installation Guide](docs/installation.md)
   - [Configuration Guide](docs/configuration.md)

2. **Development**
   - [Development Setup](docs/development.md)
   - [Contributing Guide](CONTRIBUTING.md)
   - [Testing Guide](docs/testing.md)

3. **Deployment**
   - [Docker Deployment](docs/docker-deployment.md)
   - [Kubernetes Deployment](docs/kubernetes-deployment.md)
   - [Production Checklist](docs/production-checklist.md)

4. **Operations**
   - [Monitoring Guide](docs/monitoring.md)
   - [Logging Guide](docs/logging.md)
   - [Troubleshooting Guide](docs/troubleshooting.md)

### Example Applications

1. **Basic Examples**
   - [Hello World Agent](examples/hello-world/)
   - [OpenAI Integration](examples/openai-integration/)
   - [File Processing Agent](examples/file-processing/)

2. **Advanced Examples**
   - [Multi-Agent System](examples/multi-agent/)
   - [Database Integration](examples/database-integration/)
   - [WebSocket Agent](examples/websocket-agent/)

3. **Use Cases**
   - [Content Generation](examples/content-generation/)
   - [Data Analysis](examples/data-analysis/)
   - [Customer Support](examples/customer-support/)

### API Reference

For detailed API documentation, visit:

- OpenAPI UI: `http://localhost:8080/docs`
- ReDoc UI: `http://localhost:8080/redoc`
- OpenAPI JSON: `http://localhost:8080/openapi.json`

These interactive documentation interfaces provide:

- Complete API endpoint listing
- Request/response schemas
- Example requests and responses
- Interactive API testing

## Notes:

- The API operations only affect resources in the Management API's namespace
- Authentication is required for all endpoints
- API paths are prefixed with `/api`
- The API always returns JSON responses with appropriate HTTP status codes
- The default format for all dates and times is ISO 8601 (e.g., `2023-06-15T12:34:56Z`)
