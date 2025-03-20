# AI Agent Platform Management API

> [!NOTE]
> This documentation outlines the Management API for the AI Agent Platform, which allows AI engineers to deploy and manage their CrewAI agents on Kubernetes.

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

The AI Agent Platform Management API provides a user-friendly interface for creating and managing AI Agent Runtimes. It acts as a bridge between users and the underlying Kubernetes infrastructure, translating user-friendly requests into Kubernetes Custom Resources that are processed by the platform's operator.

Key features:

- **Simple Deployment**: Deploy CrewAI agents with minimal configuration
- **Code Management**: Upload code directly or integrate with GitHub repositories
- **Environment Management**: Configure environment variables for your agents
- **Scalability**: Control resource allocation and replica count
- **Operations**: Restart and monitor your deployed agents

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

<details>
<summary>Click to expand quick start instructions</summary>

1. **Set up authentication**:

   ```bash
   # Get your API key from the platform dashboard
   export API_AUTH_TOKEN="your-auth-token-here"
   ```

2. **Deploy your first agent**:

   ```bash
   curl -X POST https://api.ai-agent-platform.example.com/api/runtimes \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
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
     -H "Authorization: Bearer ${API_AUTH_TOKEN}"
   ```

</details>

## Authentication

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

## API Endpoints

### AI Agent Runtimes

#### Create a New Runtime

**Endpoint**: `POST /api/runtimes`

Creates a new AI Agent Runtime deployment.

**Request Parameters**:

- `namespace` (optional): Kubernetes namespace (can be provided as query parameter or in request body)
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
      "value": "sk-..."
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

#### List All Runtimes

**Endpoint**: `GET /api/runtimes`

Lists all AI Agent Runtimes in the specified namespace.

**Query Parameters**:

- `namespace` (optional): Kubernetes namespace to list runtimes from

**Example**:

```bash
# List all runtimes
curl -X GET "http://localhost:8080/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# List runtimes in specific namespace
curl -X GET "http://localhost:8080/api/runtimes?namespace=my-namespace" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Get Runtime Details

**Endpoint**: `GET /api/runtimes/{name}`

Gets details of a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Query Parameters**:

- `namespace` (optional): Kubernetes namespace (can be provided as query parameter or in request body)

**Example**:

```bash
curl -X GET "http://localhost:8080/api/runtimes/content-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Delete Runtime

**Endpoint**: `DELETE /api/runtimes/{name}`

Deletes a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Query Parameters**:

- `namespace` (optional): Kubernetes namespace (can be provided as query parameter or in request body)

**Example**:

```bash
curl -X DELETE "http://localhost:8080/api/runtimes/content-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Restart Runtime

**Endpoint**: `POST /api/runtimes/{name}/restart`

Restarts a specific AI Agent Runtime.

**Path Parameters**:

- `name`: Name of the AI Agent Runtime

**Query Parameters**:

- `namespace` (optional): Kubernetes namespace (can be provided as query parameter or in request body)

**Example**:

```bash
curl -X POST "http://localhost:8080/api/runtimes/content-agent/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Create Runtime from File

**Endpoint**: `POST /api/runtimes/from-file`

Creates a new AI Agent Runtime using an uploaded code file (ZIP archive) and a runtime configuration.

**Request Parameters**:

- `runtime_config` (form field): JSON file containing the runtime configuration
- `file` (form file): ZIP archive containing the code files for the agent

**Example**:

```bash
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

Example `runtime_config.json`:

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
      "value": "sk-..."
    },
    {
      "name": "DEBUG",
      "value": "true"
    }
  ],
  "replicas": 1
}
```

### Environment Variables

Environment variables can be configured when creating or updating a runtime. They can be specified in two ways:

1. As part of the runtime creation request
2. Through Kubernetes secrets or configmaps

#### Environment Variable Configuration

When creating a runtime, you can specify environment variables in the request body:

```json
{
  "name": "my-agent",
  "description": "My agent with environment variables",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/my-agent",
      "branch": "main"
    }
  },
  "envVars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "sk-..."
    },
    {
      "name": "DEBUG",
      "value": "true"
    }
  ]
}
```

#### Using Kubernetes Secrets and ConfigMaps

For sensitive data, you can reference Kubernetes secrets:

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

Upload code directly using the `/api/runtimes/from-file` endpoint:

```bash
# Create runtime_config.json
cat > runtime_config.json << EOF
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
      "value": "sk-..."
    }
  ]
}
EOF

# Zip your code
zip -r agent_code.zip your_agent_directory/

# Upload code and configuration
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

#### ConfigMap

Use an existing Kubernetes ConfigMap as the code source:

```json
{
  "codeSource": {
    "type": "configmap",
    "configMapName": "my-agent-code"
  }
}
```

### Runtime Operations

The following operations are available for managing AI Agent Runtimes:

#### Restart Runtime

Restart a runtime to apply configuration changes or recover from errors:

```bash
curl -X POST "http://localhost:8080/api/runtimes/my-agent/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Delete Runtime

Remove a runtime and all associated resources:

```bash
curl -X DELETE "http://localhost:8080/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

#### Get Runtime Status

Check the current status of a runtime:

```bash
curl -X GET "http://localhost:8080/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

The response includes:

- Runtime phase (Pending, Running, Failed, etc.)
- Status message
- Last transition time
- Pod and service status

### Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Missing or invalid API token
- `404 Not Found`: Runtime or resource not found
- `500 Internal Server Error`: Server-side error

Example error response:

```json
{
  "detail": "Failed to create AI Agent Runtime: Invalid configuration"
}
```

Common error scenarios:

1. **Authentication Errors**

   ```bash
   # Missing token
   curl -X GET "http://localhost:8080/api/runtimes"
   # Response: {"detail":"Not authenticated"}

   # Invalid token
   curl -X GET "http://localhost:8080/api/runtimes" \
     -H "Authorization: Bearer invalid-token"
   # Response: {"detail":"Invalid authentication credentials"}
   ```

2. **Resource Not Found**

   ```bash
   curl -X GET "http://localhost:8080/api/runtimes/non-existent" \
     -H "Authorization: Bearer ${API_AUTH_TOKEN}"
   # Response: {"detail":"AI Agent Runtime not found: non-existent"}
   ```

3. **Invalid Configuration**

   ```bash
   curl -X POST "http://localhost:8080/api/runtimes" \
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

### Best Practices

1. **Authentication**
   - Store API tokens securely
   - Rotate tokens periodically
   - Use environment variables for token storage

2. **Environment Variables**
   - Use Kubernetes secrets for sensitive data
   - Use ConfigMaps for non-sensitive configuration
   - Follow the principle of least privilege

3. **Code Management**
   - Use version control (Git) for production deployments
   - Keep code archives small and focused
   - Include only necessary files in uploads

4. **Error Handling**
   - Implement proper error handling in your code
   - Check API responses for error messages
   - Use appropriate HTTP status codes

5. **Resource Management**
   - Set appropriate resource limits
   - Monitor resource usage
   - Clean up unused runtimes

## Implementation Examples

### Creating a Simple Runtime

Here's an example of creating a basic AI Agent Runtime:

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
      "valueFrom": {
        "secretKeyRef": {
          "name": "api-keys",
          "key": "openai"
        }
      }
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
curl -X POST "http://localhost:8080/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d @runtime_config.json
```

### File Upload Deployment

Example of deploying an agent using file upload:

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
      "value": "sk-..."
    }
  ]
}
EOF

# Zip the agent code
zip -r agent_code.zip my-agent/

# Upload code and configuration
curl -X POST "http://localhost:8080/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

### Using Git Repository with Authentication

Example of creating a runtime using a private Git repository:

```bash
cat > runtime_config.json << EOF
{
  "name": "git-agent",
  "description": "Agent from private Git repo",
  "entrypoint": "src/main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/private-agent",
      "branch": "main",
      "auth": {
        "type": "token",
        "token": "github_pat_..."
      }
    }
  },
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
EOF

curl -X POST "http://localhost:8080/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d @runtime_config.json
```

### Managing Environment Variables

Example of using different types of environment variables:

```bash
# Using direct values
cat > runtime_config.json << EOF
{
  "name": "env-agent",
  "description": "Agent with various env vars",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/env-agent",
      "branch": "main"
    }
  },
  "envVars": [
    {
      "name": "DEBUG",
      "value": "true"
    },
    {
      "name": "LOG_LEVEL",
      "value": "INFO"
    }
  ]
}
EOF

# Using Kubernetes secrets and configmaps
cat > runtime_config.json << EOF
{
  "name": "secure-agent",
  "description": "Agent with secure env vars",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/username/secure-agent",
      "branch": "main"
    }
  },
  "envVars": [
    {
      "name": "API_KEY",
      "valueFrom": {
        "secretKeyRef": {
          "name": "api-keys",
          "key": "service-api"
        }
      }
    },
    {
      "name": "CONFIG",
      "valueFrom": {
        "configMapKeyRef": {
          "name": "app-config",
          "key": "config.json"
        }
      }
    }
  ]
}
EOF
```

### Runtime Operations

Examples of common runtime operations:

```bash
# List all runtimes
curl -X GET "http://localhost:8080/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# Get specific runtime details
curl -X GET "http://localhost:8080/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# Restart a runtime
curl -X POST "http://localhost:8080/api/runtimes/my-agent/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"

# Delete a runtime
curl -X DELETE "http://localhost:8080/api/runtimes/my-agent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

### Error Handling Examples

Examples of handling common errors:

```bash
# Missing authentication
curl -X GET "http://localhost:8080/api/runtimes"
# Response: {"detail":"Not authenticated"}

# Invalid runtime name
curl -X GET "http://localhost:8080/api/runtimes/non-existent" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
# Response: {"detail":"AI Agent Runtime not found: non-existent"}

# Invalid configuration
curl -X POST "http://localhost:8080/api/runtimes" \
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

These examples demonstrate the most common use cases and patterns for working with the Management API. They can be used as templates for your own implementations.

## Environment Configuration

The Management API can be configured using environment variables. Here are the available configuration options:

### API Authentication

- `API_AUTH_ENABLED`: Enable/disable API authentication (default: `true`)
- `API_AUTH_TOKEN`: The authentication token for API requests

Example configuration:

```bash
# Enable authentication and set token
export API_AUTH_ENABLED=true
export API_AUTH_TOKEN=your-secure-token

# Or in .env file
API_AUTH_ENABLED=true
API_AUTH_TOKEN=your-secure-token
```

### Server Configuration

- `API_HOST`: Host to bind the server to (default: `0.0.0.0`)
- `API_PORT`: Port to listen on (default: `8080`)
- `API_DEBUG`: Enable debug mode (default: `false`)

Example configuration:

```bash
# Configure server
export API_HOST=localhost
export API_PORT=8080
export API_DEBUG=true

# Or in .env file
API_HOST=localhost
API_PORT=8080
API_DEBUG=true
```

### Kubernetes Configuration

- `KUBERNETES_NAMESPACE`: Default namespace for runtime deployments (default: `default`)
- `KUBERNETES_CONFIG_PATH`: Path to kubeconfig file (optional)
- `KUBERNETES_CONTEXT`: Kubernetes context to use (optional)

Example configuration:

```bash
# Configure Kubernetes settings
export KUBERNETES_NAMESPACE=ai-agents
export KUBERNETES_CONFIG_PATH=/path/to/kubeconfig
export KUBERNETES_CONTEXT=my-cluster

# Or in .env file
KUBERNETES_NAMESPACE=ai-agents
KUBERNETES_CONFIG_PATH=/path/to/kubeconfig
KUBERNETES_CONTEXT=my-cluster
```

### Resource Defaults

- `DEFAULT_CPU_REQUEST`: Default CPU request for runtimes (default: `100m`)
- `DEFAULT_MEMORY_REQUEST`: Default memory request for runtimes (default: `256Mi`)
- `DEFAULT_CPU_LIMIT`: Default CPU limit for runtimes (default: `500m`)
- `DEFAULT_MEMORY_LIMIT`: Default memory limit for runtimes (default: `512Mi`)

Example configuration:

```bash
# Configure resource defaults
export DEFAULT_CPU_REQUEST=200m
export DEFAULT_MEMORY_REQUEST=512Mi
export DEFAULT_CPU_LIMIT=1000m
export DEFAULT_MEMORY_LIMIT=1Gi

# Or in .env file
DEFAULT_CPU_REQUEST=200m
DEFAULT_MEMORY_REQUEST=512Mi
DEFAULT_CPU_LIMIT=1000m
DEFAULT_MEMORY_LIMIT=1Gi
```

### Storage Configuration

- `STORAGE_CLASS`: Storage class for persistent volumes (default: `standard`)
- `DEFAULT_STORAGE_SIZE`: Default storage size for runtimes (default: `1Gi`)

Example configuration:

```bash
# Configure storage settings
export STORAGE_CLASS=fast-ssd
export DEFAULT_STORAGE_SIZE=5Gi

# Or in .env file
STORAGE_CLASS=fast-ssd
DEFAULT_STORAGE_SIZE=5Gi
```

### Logging Configuration

- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_FORMAT`: Logging format (`json` or `text`, default: `json`)

Example configuration:

```bash
# Configure logging
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text

# Or in .env file
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Using Environment Files

You can use a `.env` file to configure the API. Create a file named `.env` in the root directory:

```bash
# API Authentication
API_AUTH_ENABLED=true
API_AUTH_TOKEN=your-secure-token

# Server Configuration
API_HOST=localhost
API_PORT=8080
API_DEBUG=false

# Kubernetes Configuration
KUBERNETES_NAMESPACE=ai-agents
KUBERNETES_CONFIG_PATH=/path/to/kubeconfig
KUBERNETES_CONTEXT=my-cluster

# Resource Defaults
DEFAULT_CPU_REQUEST=200m
DEFAULT_MEMORY_REQUEST=512Mi
DEFAULT_CPU_LIMIT=1000m
DEFAULT_MEMORY_LIMIT=1Gi

# Storage Configuration
STORAGE_CLASS=fast-ssd
DEFAULT_STORAGE_SIZE=5Gi

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Environment Configuration

When running the API in Docker, you can pass environment variables using the `-e` flag or an environment file:

```bash
# Using individual environment variables
docker run -d \
  -e API_AUTH_TOKEN=your-secure-token \
  -e KUBERNETES_NAMESPACE=ai-agents \
  -e LOG_LEVEL=INFO \
  -p 8080:8080 \
  ai-agent-platform/management-api

# Using an environment file
docker run -d \
  --env-file .env \
  -p 8080:8080 \
  ai-agent-platform/management-api
```

### Kubernetes Deployment Configuration

When deploying the API to Kubernetes, you can use ConfigMaps and Secrets to manage environment variables:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: management-api-config
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8080"
  KUBERNETES_NAMESPACE: "ai-agents"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
---
apiVersion: v1
kind: Secret
metadata:
  name: management-api-secrets
type: Opaque
data:
  API_AUTH_TOKEN: <base64-encoded-token>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: management-api
spec:
  template:
    spec:
      containers:
      - name: management-api
        envFrom:
        - configMapRef:
            name: management-api-config
        - secretRef:
            name: management-api-secrets
```

## Security Considerations

When configuring the Management API, consider these security best practices:

1. **API Authentication**
   - Always enable authentication in production
   - Use strong, randomly generated tokens
   - Rotate tokens periodically
   - Store tokens securely using Kubernetes secrets

2. **Network Security**
   - Configure TLS for production deployments
   - Use network policies to restrict access
   - Consider running behind a reverse proxy

3. **Resource Limits**
   - Set appropriate resource limits to prevent DoS
   - Monitor resource usage
   - Implement rate limiting for API endpoints

4. **Access Control**
   - Use RBAC for Kubernetes access
   - Limit API permissions to required resources
   - Regularly audit access patterns

5. **Logging and Monitoring**
   - Enable appropriate logging levels
   - Monitor API usage and errors
   - Set up alerts for security events

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

### Version History

For a complete list of changes and version history, see the [CHANGELOG.md](CHANGELOG.md) file.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:

- Submit bug reports and feature requests
- Set up your development environment
- Submit pull requests
- Follow our coding standards
- Run tests and linting

### Support

If you need help or have questions:

1. Check the [Documentation](docs/)
2. Search [Issues](https://github.com/username/ai-agent-platform/issues)
3. Join our [Community Chat](https://discord.gg/ai-agent-platform)
4. Email support: <support@ai-agent-platform.com>

### Roadmap

See our [public roadmap](ROADMAP.md) for planned features and improvements.
