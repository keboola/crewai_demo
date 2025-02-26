# Azure OpenAI Integration

> [!NOTE]
> This document explains how to use Azure OpenAI with the CrewAI Content Orchestrator.

## Table of Contents
- [Overview](#overview)
- [Configuration](#configuration)
- [Implementation Details](#implementation-details)
- [API Key Compatibility](#api-key-compatibility)
- [Troubleshooting](#troubleshooting)

## Overview

The CrewAI Content Orchestrator supports both OpenRouter and Azure OpenAI as LLM providers. This gives you flexibility in choosing your preferred provider based on your needs.

## Configuration

To use Azure OpenAI, you need to set the following environment variables:

1. `LLM_PROVIDER=azure` - This tells the system to use Azure OpenAI instead of OpenRouter
2. `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
3. `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL (e.g., "https://your-resource-name.openai.azure.com/")
4. `AZURE_OPENAI_API_VERSION` - (Optional) The API version to use (defaults to "2023-05-15")
5. `AZURE_OPENAI_DEPLOYMENT_ID` - (Optional) The deployment ID to use (defaults to "gpt-35-turbo-0125")

You can set these variables in your `.env` file:

```bash
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15  # Optional
AZURE_OPENAI_DEPLOYMENT_ID=gpt-35-turbo-0125  # Optional
```

A sample configuration file is provided in `.env.azure.sample`.

## Implementation Details

The system uses the `AzureChatOpenAI` class from `langchain_openai` when `LLM_PROVIDER` is set to `azure`. This class is specifically designed to work with Azure OpenAI deployments and handles the authentication and API calls differently from the standard OpenAI integration.

Here's how the implementation works in the `crewai_app/orchestrator.py` file:

```python
if llm_provider == "azure":
    # Azure OpenAI configuration
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
    deployment_id = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-35-turbo-0125")
    
    if not api_key or not azure_endpoint:
        raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set for Azure OpenAI")
    
    return AzureChatOpenAI(
        azure_deployment=deployment_id,
        openai_api_version=api_version,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        temperature=0.7,
    )
```

## API Key Compatibility

When using OpenRouter, only the `OPENAI_API_KEY` needs to be set. This is for compatibility with libraries like LiteLLM that expect this environment variable.

When using Azure OpenAI, you need to set the `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` variables.

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Make sure your `AZURE_OPENAI_API_KEY` is correct
   - Check that your `AZURE_OPENAI_ENDPOINT` is properly formatted (should end with `.openai.azure.com/`)

2. **Model Not Found**
   - Verify that the `AZURE_OPENAI_DEPLOYMENT_ID` matches a deployment in your Azure OpenAI resource
   - Check the Azure OpenAI Studio to see available deployments

3. **API Version Error**
   - If you get API version errors, try updating the `AZURE_OPENAI_API_VERSION` to a more recent version
   - Azure OpenAI API versions change periodically

### Testing Azure OpenAI

You can test your Azure OpenAI configuration with the following curl command:

```bash
curl -X POST "https://your-resource-name.openai.azure.com/openai/deployments/your-deployment-id/chat/completions?api-version=2023-05-15" \
  -H "Content-Type: application/json" \
  -H "api-key: your-azure-api-key" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, world!"}
    ]
  }'
```

Replace the placeholders with your actual values.

## Deployment IDs

Azure OpenAI uses deployment IDs instead of model names. The default deployment ID is `gpt-35-turbo-0125`, but you can specify a different one by setting the `AZURE_OPENAI_DEPLOYMENT_ID` environment variable.

Supported deployment IDs include:

- `gpt-35-turbo-0125` - GPT-3.5 Turbo
- `gpt-4-32k` - GPT-4 with 32k context window

The deployment ID must match a deployment in your Azure OpenAI resource.

## Testing the Integration

You can test the Azure OpenAI integration using the provided test scripts:

```bash
# Test Azure OpenAI directly
python test_azure_openai.py

# Test OpenRouter directly
python test_openrouter.py

# Test the integration with CrewAI
python test_crewai_integration.py
```

## Switching Between Providers

You can easily switch between OpenRouter and Azure OpenAI by changing the `LLM_PROVIDER` environment variable:

- For OpenRouter: `LLM_PROVIDER=openrouter`
- For Azure OpenAI: `LLM_PROVIDER=azure`

Make sure you have the appropriate API keys set for the provider you're using.

### OpenRouter Configuration

For OpenRouter, you can set the following environment variables:

```bash
LLM_PROVIDER=openrouter
OPENAI_API_KEY=your-api-key
OPENAI_API_BASE=https://openrouter.ai/api/v1  # Optional, this is the default
OPENROUTER_MODEL=openai/gpt-4o-mini  # Optional, this is the default
```

Note that OpenRouter model IDs follow the format `provider/model-name`, such as:

- `openai/gpt-4o-mini`
- `openai/gpt-4`
- `anthropic/claude-3.5-sonnet`

## API Key Compatibility

When using OpenRouter, you only need to set the `OPENAI_API_KEY` environment variable. This ensures compatibility with libraries like LiteLLM that expect the standard OpenAI API key to be set:

```python
# Use OPENAI_API_KEY directly for compatibility with all libraries
api_key = os.environ.get("OPENAI_API_KEY")
```

For more information about Azure OpenAI, refer to the [official documentation](https://learn.microsoft.com/en-us/fabric/data-science/ai-services/how-to-use-openai-sdk-synapse?tabs=python0).
