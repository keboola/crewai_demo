# 🤖 AI Agent Platform: Quickstart Guide

> [!NOTE]
> This quickstart guide will help you get up and running with the AI Agent Platform quickly. For more detailed information, refer to the specific guides linked throughout this document.

## Prerequisites

Before you begin, ensure you have the following:

- Docker installed (for local development)
- Kubernetes cluster (for production deployment)
- Access to the Management API endpoint
- API token for authentication

## Step 1: Deploy Your First AI Agent

The quickest way to deploy an AI agent is to use a pre-built example. This example demonstrates a simple content creation agent:

```bash
# Set your API token
export API_AUTH_TOKEN="your-auth-token-here"

# Create a runtime for a content creation agent
curl -X POST "https://agentic.canary-orion.keboola.dev/api/runtimes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_AUTH_TOKEN}" \
  -d '{
    "name": "content-agent",
    "description": "Simple content creation agent",
    "code_source": {
      "type": "git",
      "git_repository": "https://github.com/keboola/agentic-content-creator.git",
      "git_reference": "main"
    },
    "environment_variables": {
      "OPENAI_API_KEY": "sk-..."
    }
  }'
```

You'll receive a response with the runtime details, including the runtime URL.

## Step 2: Interact with Your AI Agent

Once your runtime is deployed, you can interact with it using the Runtime API:

```bash
# Set your runtime URL (replace with your actual runtime URL)
export RUNTIME_URL="https://content-agent.agentic.canary-orion.keboola.dev"

# Start a run to create content
curl -X POST "${RUNTIME_URL}/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a blog post about AI agents",
    "parameters": {
      "word_count": 500,
      "tone": "informative"
    }
  }'
```

This will return a run ID that you can use to track the progress of your request.

## Step 3: Check Run Status

Monitor the status of your run:

```bash
# Replace RUN_ID with the ID from the previous response
curl "${RUNTIME_URL}/run/RUN_ID"
```

## Step 4: Retrieve Results

Once the run is complete, retrieve the results:

```bash
# Replace RUN_ID with your run ID
curl "${RUNTIME_URL}/run/RUN_ID/result"
```

## Next Steps

Now that you've deployed and interacted with your first AI agent, you can:

- [Explore more complex examples](examples/content-creation-example.md)
- [Deploy a custom agent](deployment/docker-deployment.md)
- [Configure advanced options](configuration/)
- [Set up human-in-the-loop workflows](../api/runtime-api.md#human-in-the-loop-workflows)

## Troubleshooting

If you encounter issues:

- Check that your API token is valid
- Verify that your runtime is in the "RUNNING" state
- Review the [Runtime API documentation](../api/runtime-api.md) for correct endpoints
- See the [Troubleshooting guide](troubleshooting/) for common issues

---

**Last Updated:** March 24, 2024 