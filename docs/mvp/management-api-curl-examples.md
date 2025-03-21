# Management API Curl Examples

This document provides practical examples of interacting with the AI Agent Platform Management API using curl commands. These examples demonstrate common operations for managing AI Agent Runtimes.

## Prerequisites

- Access to the Management API (at `https://agentic.canary-orion.keboola.dev`)
- An API token for authentication
- Access to a terminal with `curl` installed

```bash
# Set your API token as an environment variable
export API_AUTH_TOKEN="your-auth-token-here"
```

## Runtime Management

### 1. Create a Runtime (Dry Run)

Create a runtime manifest without applying it to the cluster:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes?dry_run=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "name": "curl-demo-runtime",
    "description": "Demo runtime created via curl",
    "entrypoint": "orchestrator.py",
    "codeSource": {
      "type": "git",
      "gitRepo": {
        "url": "https://github.com/keboola/crewai_demo.git",
        "branch": "main"
      }
    },
    "envVars": [
      {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "replicas": 1
  }'
```

### 2. Create a Runtime on the Cluster

Create and deploy an AI Agent Runtime:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "name": "curl-demo-runtime",
    "description": "Demo runtime created via curl",
    "entrypoint": "orchestrator.py",
    "codeSource": {
      "type": "git",
      "gitRepo": {
        "url": "https://github.com/keboola/crewai_demo.git",
        "branch": "main"
      }
    },
    "envVars": [
      {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "replicas": 1
  }'
```

Response:

```json
{
  "name": "curl-demo-runtime",
  "url": "https://curl-demo-runtime.agentic.canary-orion.keboola.dev",
  "status": "creating",
  "message": "AI Agent Runtime created successfully"
}
```

### 3. Create a Runtime in a Specific Namespace

Create a runtime in a specific namespace:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "namespace": "foobar",
    "name": "curl-demo-runtime",
    "description": "Demo runtime created via curl",
    "entrypoint": "orchestrator.py",
    "codeSource": {
      "type": "git",
      "gitRepo": {
        "url": "https://github.com/keboola/crewai_demo.git",
        "branch": "main"
      }
    },
    "envVars": [
      {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "replicas": 1
  }'
```

### 4. Get a List of Runtimes

Retrieve all runtimes from the default namespace:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "runtimes": [
    {
      "name": "curl-demo-runtime",
      "status": "running",
      "url": "https://curl-demo-runtime.agentic.canary-orion.keboola.dev",
      "created_at": "2023-06-15T12:34:56Z"
    },
    {
      "name": "another-runtime",
      "status": "running",
      "url": "https://another-runtime.agentic.canary-orion.keboola.dev",
      "created_at": "2023-06-14T10:22:45Z"
    }
  ]
}
```

### 5. Get a List of Runtimes from a Specific Namespace

Retrieve all runtimes from a specific namespace:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "namespace": "foobar"
  }'
```

### 6. Get a Specific Runtime

Retrieve a specific runtime by name from the default namespace:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/curl-demo-runtime" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "name": "curl-demo-runtime",
  "description": "Demo runtime created via curl",
  "url": "https://curl-demo-runtime.agentic.canary-orion.keboola.dev",
  "status": "running",
  "entrypoint": "orchestrator.py",
  "codeSource": {
    "type": "git",
    "gitRepo": {
      "url": "https://github.com/keboola/crewai_demo.git",
      "branch": "main"
    }
  },
  "envVars": [
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
      "cpu": "500m",
      "memory": "512Mi"
    },
    "requests": {
      "cpu": "100m",
      "memory": "256Mi"
    }
  },
  "created_at": "2023-06-15T12:34:56Z",
  "updated_at": "2023-06-15T12:40:22Z"
}
```

### 7. Get a Runtime from a Specific Namespace

Retrieve a runtime from a specific namespace:

```bash
curl -X GET "https://agentic.canary-orion.keboola.dev/api/runtimes/curl-demo-runtime" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "namespace": "foobar"
  }'
```

### 8. Delete a Runtime

Delete a runtime from the default namespace:

```bash
curl -X DELETE "https://agentic.canary-orion.keboola.dev/api/runtimes/curl-demo-runtime" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "message": "AI Agent Runtime 'curl-demo-runtime' deleted successfully"
}
```

### 9. Delete a Runtime from a Specific Namespace

Delete a runtime from a specific namespace:

```bash
curl -X DELETE "https://agentic.canary-orion.keboola.dev/api/runtimes/curl-demo-runtime" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "namespace": "foobar"
  }'
```

### 10. Restart a Runtime

Restart a runtime in the default namespace:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/curl-demo-runtime/restart" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}"
```

Response:

```json
{
  "message": "AI Agent Runtime 'curl-demo-runtime' restarted successfully"
}
```

## Advanced Configuration Examples

### 11. Create a Runtime with Advanced Options

Create a runtime with more configuration options in the default namespace:

```bash
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "name": "advanced-runtime",
    "description": "Advanced runtime with more configuration",
    "entrypoint": "src/main.py",
    "codeSource": {
      "type": "git",
      "gitRepo": {
        "url": "https://github.com/keboola/crewai_demo.git",
        "branch": "develop",
        "auth": {
          "type": "token",
          "token": "ghp_your_token_here"
        }
      }
    },
    "envVars": [
      {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
      {"name": "LOG_LEVEL", "value": "DEBUG"},
      {"name": "API_HOST", "value": "0.0.0.0"},
      {"name": "API_PORT", "value": "8000"}
    ],
    "resources": {
      "limits": {
        "cpu": "1",
        "memory": "2Gi"
      },
      "requests": {
        "cpu": "500m", 
        "memory": "1Gi"
      }
    },
    "replicas": 2
  }'
```

### 12. Create a Runtime with File Upload

Create a runtime from a ZIP file containing your code:

```bash
# First, create a runtime configuration JSON file
cat > runtime_config.json << EOF
{
  "name": "file-upload-runtime",
  "description": "Runtime created from file upload",
  "entrypoint": "main.py",
  "codeSource": {
    "type": "inline"
  },
  "envVars": [
    {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
    {"name": "DEBUG", "value": "true"}
  ],
  "replicas": 1
}
EOF

# Then upload the file and configuration
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes/from-file" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=@runtime_config.json" \
  -F "file=@agent_code.zip"
```

Response:

```json
{
  "name": "file-upload-runtime",
  "url": "https://file-upload-runtime.agentic.canary-orion.keboola.dev",
  "status": "creating",
  "message": "AI Agent Runtime created successfully from file upload"
}
```

## Accessing the Runtime API

After the runtime is created and deployed, you can access the runtime API:

```bash
# The runtime API is available at:
https://curl-demo-runtime.agentic.canary-orion.keboola.dev
```

## API Schema

The API expects payloads with the following structure:

### Runtime Creation Request

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `namespace` | string | Kubernetes namespace to use | No |
| `name` | string | Name of the AI Agent Runtime | Yes |
| `description` | string | Description of the AI Agent Runtime | No |
| `entrypoint` | string | Path to the entry Python file | Yes |
| `codeSource` | object | Configuration for the source of the code | Yes |
| `envVars` | array | Environment variables for the AI agent | No |
| `resources` | object | CPU and memory resource requirements | No |
| `replicas` | integer | Number of replicas (default: 1) | No |

### codeSource Object Structure

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | string | Source type: `git` or `inline` | Yes |
| `gitRepo` | object | Git repository configuration (when type is `git`) | No* |

\* Required when type is "git"

### gitRepo Object Structure

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `url` | string | URL of the Git repository | Yes |
| `branch` | string | Branch to checkout (default: `main`) | No |
| `auth` | object | Authentication configuration | No |

### envVars Array Structure

Each item in the array has the following structure:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Name of the environment variable | Yes |
| `value` | string | Value of the environment variable | No* |
| `secure` | boolean | Whether to store the variable securely in a Secret | No |
| `valueFrom` | object | Reference to a Kubernetes Secret or ConfigMap | No* |

\* Either `value` or `valueFrom` must be provided

## Notes

- Field names use camelCase formatting (e.g., `codeSource`, not `code_source`)
- The API uses standard HTTP status codes to indicate success or failure
- Secure environment variables (marked with `secure: true`) are stored in Kubernetes Secrets
- By default, the API uses the default namespace configured in the Management API service
- For secure operations in production, always use HTTPS and proper authentication
