# Management API Curl Examples

This document provides practical examples of interacting with the AI Agent Platform Management API using curl commands.
These examples demonstrate common operations for managing AI Agent Runtimes.

## Prerequisites

- The Management API must be running (typically at `http://localhost:8000`)
- You need access to a terminal with `curl` installed

## Runtime Management

### 1. Create a Runtime (Dry Run)

Creates a runtime manifest without applying it to the cluster:

```bash
curl -X POST "http://localhost:8000/api/runtimes?dry_run=true" \
  -H "Content-Type: application/json" \
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

Creates and deploys an AI Agent Runtime:

```bash
curl -X POST "http://localhost:8000/api/runtimes" \
  -H "Content-Type: application/json" \
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

### 3. Create a Runtime in a Specific Namespace

Creates a runtime in the specified namespace using the request body approach:

```bash
curl -X POST "http://localhost:8000/api/runtimes" \
  -H "Content-Type: application/json" \
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

### 4. Get a List of Runtimes (Default Namespace)

Retrieves all runtimes from the default namespace:

```bash
curl -X GET "http://localhost:8000/api/runtimes"
```

### 4a. Get a List of Runtimes from a Specific Namespace (Request Body - Recommended)

Retrieves all runtimes from a specific namespace using the request body approach (recommended):

```bash
curl -X GET "http://localhost:8000/api/runtimes" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "foobar"
  }'
```

### 5. Get a Specific Runtime (Default Namespace)

Retrieves a specific runtime by name from the default namespace:

```bash
curl -X GET "http://localhost:8000/api/runtimes/curl-demo-runtime"
```

### 6a. Get a Runtime from a Specific Namespace (Request Body - Recommended)

Retrieves a runtime from a specific namespace using the request body approach (recommended):

```bash
curl -X GET "http://localhost:8000/api/runtimes/curl-demo-runtime" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "foobar"
  }'
```

### 7. Delete a Runtime (Default Namespace)

Deletes a runtime from the default namespace:

```bash
curl -X DELETE "http://localhost:8000/api/runtimes/curl-demo-runtime"
```

### 8a. Delete a Runtime from a Specific Namespace (Request Body - Recommended)

Deletes a runtime from a specific namespace using the request body approach (recommended):

```bash
curl -X DELETE "http://localhost:8000/api/runtimes/curl-demo-runtime" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "foobar"
  }'
```

## Advanced Configuration Examples

### 9. Create a Runtime with Advanced Options (Default Namespace)

Creates a runtime with more configuration options in the default namespace:

```bash
curl -X POST "http://localhost:8000/api/runtimes" \
  -H "Content-Type: application/json" \
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

### 9a. Create a Runtime with Advanced Options in a Specific Namespace (Request Body - Recommended)

Creates a runtime with more configuration options in a specific namespace:

```bash
curl -X POST "http://localhost:8000/api/runtimes" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "foobar",
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

## Accessing the Runtime API

After the runtime is created and the operator deploys it, you can access the runtime API:

### Port-Forward to Access the Runtime API Locally

```bash
kubectl port-forward -n foobar service/curl-demo-runtime 8080:80
```

Then access it at `http://localhost:8080/api/`.

## Payload Structure

The API expects payloads with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `namespace` | string | (Optional) Kubernetes namespace to use. If not provided, default namespace will be used. |
| `name` | string | Name of the AI Agent Runtime |
| `description` | string | Description of the AI Agent Runtime |
| `entrypoint` | string | Path to the entry Python file |
| `codeSource` | object | Configuration for the source of the code |
| `envVars` | array | Environment variables for the AI agent |
| `resources` | object | CPU and memory resource requirements |
| `replicas` | integer | Number of replicas (default: 1) |

### codeSource Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Source type: `git`, `configMap`, or `inline` |
| `gitRepo` | object | Git repository configuration (when type is `git`) |

### gitRepo Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | URL of the Git repository |
| `branch` | string | Branch to checkout (default: `main`) |
| `auth` | object | Authentication configuration |

### envVars Array Structure

Each item in the array has the following structure:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Name of the environment variable |
| `value` | string | Value of the environment variable |
| `secure` | boolean | Whether to store the variable securely in a Secret |

## Notes

- All field names use camelCase formatting (e.g., `codeSource`, not `code_source`)
- The API uses standard HTTP status codes to indicate success or failure
- Secure environment variables (marked with `secure: true`) are stored in Kubernetes Secrets
- The namespace can be specified either as a query parameter (deprecated) or in the request body (recommended)
- If namespace is not specified, the API's configured default namespace will be used
