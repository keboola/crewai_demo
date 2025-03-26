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

### 2. Create a Runtime

Create a runtime:

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

### 3. Get a List of Runtimes

Retrieve all runtimes in the Management API's namespace:

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

### 4. Get a Runtime by Name

Retrieve a specific runtime by name:

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

### 5. Delete a Runtime

Delete a runtime:

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

### 6. Restart a Runtime

Restart a runtime:

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

### 7. Create a Runtime with Advanced Options

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

### 8. Creating a Runtime from File Upload

You can also create runtimes by uploading code files directly:

```bash
# Create a runtime configuration JSON file
cat > runtime_config.json << EOF
{
  "name": "file-upload-runtime",
  "description": "Runtime created from file upload",
  "entrypoint": "main.py",
  "code_source": {
    "type": "file"
  },
  "env_vars": [
    {"name": "OPENAI_API_KEY", "value": "sk-your-key-here", "secure": true},
    {"name": "DEBUG", "value": "true"}
  ],
  "replicas": 1
}
EOF

# Method 1: Using $(cat) to pass the JSON as a string
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config=$(cat runtime_config.json)" \
  -F "code_file=@agent_code.zip"

# Method 2: Uploading the config as a separate file
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -F "runtime_config_file=@runtime_config.json" \
  -F "code_file=@agent_code.zip"
```

> [!NOTE]
> The legacy endpoint `POST /api/runtimes/from-file` is still available but deprecated. It works the same way but uses `file` instead of `code_file` as the parameter name.

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

For more information on how to use the Runtime API, see the [Runtime API Documentation](../runtime-api.md).

Last Updated: March 26, 2025 