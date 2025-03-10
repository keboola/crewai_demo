# AI Agent Wrapper Orchestration

> **Note:** This documentation covers the AI Agent Wrapper orchestration for the Keboola platform.

Raw documentation is available at [Keboola API Documentation](https://api.canary-orion.keboola.dev/#tag--Data-Apps), section **Sandboxes Service API**.

Exact Swagger API spec for Data Apps on Canary Orion Keboola stack is available at [Swagger YAML](https://data-science.canary-orion.keboola.dev/docs/swagger.yaml).

## Table of Contents

- [Authentication](#authentication)
  - [Get Keboola Manage API Token](#get-keboola-manage-api-token)
  - [Get Storage API Token](#get-storage-api-token)
- [Orchestration](#orchestration)
- [Create new Data App with AI Agent Wrapper](#create-new-data-app-with-ai-agent-wrapper)
  - [Encrypting Secrets](#encrypting-secrets)
  - [Payload Examples](#payload-examples)
  - [Creating the Data App](#creating-the-data-app)
  - [Managing the Data App](#managing-the-data-app)

## Authentication

You need both a Keboola Manage API Token and a Storage API Token.

### Get Keboola Manage API Token

1. In the upper right corner of Keboola, click your profile picture, and select **My Account & Organization**.
2. Click **Access Tokens**.
3. Click **New token**.
4. Enter your password, if prompted.
   - If you don't have a password, you can get one by clicking **Forgot your password?**.
5. Enter a name for the token and its validity period.
6. Click **Create Token**.
7. Save the token securely.

### Get Storage API Token

1. In the upper right corner of Keboola, click your profile picture, and select **Project Settings**.
2. Click **API Tokens**.
3. Hover over the user you want to generate the token for, click **...** and select **Refresh token**.
4. Confirm by clicking **Refresh token**.
5. Save the token securely.

> **Important:** Storage API Token is valid until refreshed.

## Orchestration

Set the following environment variables:

```bash
export KBC_MANAGE_API_TOKEN=<your-keboola-manage-api-token>
export KBC_STORAGE_API_TOKEN=<your-storage-api-token>
export KBC_PROJECT_ID="15" # Rohlik CrewAI Playground
```

## Create new Data App with AI Agent Wrapper

### Encrypting Secrets

Before creating a Data App, you need to encrypt any sensitive information like API keys. Use the Keboola encryption API:

```bash
curl \
  --location \
  --request POST "https://encryption.canary-orion.keboola.dev/encrypt?projectId=${KBC_PROJECT_ID}&componentId=keboola.data-apps" \
  --header 'Content-Type: text/plain' \
  --data-raw "${OPENAI_API_KEY}"
```

Save the output as `OPENAI_API_KEY_ENCRYPTED` for use in your configuration:

```bash
export OPENAI_API_KEY_ENCRYPTED="your-encrypted-key-from-response"
```

Repeat this process for any other secrets you need to encrypt (Anthropic API key, etc.).

### Payload Examples

#### Payload with GitHub repository and OpenAI secret using OpenRouter

This example shows how to configure a Data App that uses a GitHub repository and OpenAI via OpenRouter:

```json
{
  "parameters": {
    "size": "tiny",
    "imageVersion": "dev-michalkozak-agent-poc-9",
    "autoSuspendAfterSeconds": 86400,
    "dataApp": {
      "slug": "<your-data-app-slug>",
      "streamlit": {
        "config.toml": "[theme]\nfont = \"sans serif\"\ntextColor = \"#222529\"\nbackgroundColor = \"#FFFFFF\"\nsecondaryBackgroundColor = \"#E6F2FF\"\nprimaryColor = \"#1F8FFF\""
      },
      "git": {
        "repository": "<your-git-repository, i.e. https://github.com/rohlik-group/convo_newsletter_crew>",
        "branch": "<your-branch, i.e. main>",
        "entrypoint": "<your-entrypoint>, i.e. src/convo_newsletter_crew/main.py"
      },
      "secrets": {
        "#OPENAI_API_KEY": "${OPENAI_API_KEY_ENCRYPTED}",
        "OPENAI_API_BASE": "https://openrouter.ai/api/v1",
        "OPENROUTER_MODEL": "openai/gpt-4o-mini"
      }
    }
  },
  "authorization": {
    "app_proxy": {
      "auth_providers": [],
      "auth_rules": [
        {
          "type": "pathPrefix",
          "value": "/",
          "auth_required": false
        }
      ]
    }
  }
}
```

#### Payload with in-line code and Anthropic secret

This example shows how to configure a Data App with in-line code and Anthropic API:

```json
{
  "parameters": {
    "size": "tiny",
    "imageVersion": "dev-michalkozak-agent-poc-9",
    "autoSuspendAfterSeconds": 86400,
    "dataApp": {
      "slug": "<your-data-app-slug>",
      "streamlit": {
        "config.toml": "[theme]\nfont = \"sans serif\"\ntextColor = \"#222529\"\nbackgroundColor = \"#FFFFFF\"\nsecondaryBackgroundColor = \"#E6F2FF\"\nprimaryColor = \"#1F8FFF\""
      },
      "secrets": {
        "#ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY_ENCRYPTED}"
      }
    },
    "script": [
      "<your-inline-code>"
    ]
  },
  "authorization": {
    "app_proxy": {
      "auth_providers": [],
      "auth_rules": [
        {
          "type": "pathPrefix",
          "value": "/",
          "auth_required": false
        }
      ]
    }
  }
}
```

### Creating the Data App

To make the process more manageable, you can use a bash heredoc to store the complex JSON configuration and then insert it as the value for the `config` key in the curl command:

```bash
# Store the configuration in a variable using heredoc
read -r -d '' CONFIG_JSON << 'EOF'
{
  "parameters": {
    "size": "tiny",
    # ... your configuration here ...
  }
}
EOF

# Create the full payload with jq (requires jq to be installed)
PAYLOAD=$(jq -n \
  --arg config "$CONFIG_JSON" \
  '{
    "type": "streamlit",
    "name": "CrewAI Demo",
    "branchId": null,
    "description": "",
    "config": $config | fromjson
  }')

# Use the payload in the curl command
curl -X POST "https://data-science.canary-orion.keboola.dev/apps" \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}" \
  -d "$PAYLOAD"
```

This approach uses `jq` to properly handle the JSON nesting, ensuring that the `config` key correctly receives the complex JSON configuration.

Upon successful creation, you'll get a response with the Data App details:

```json
{
  "id": "string",
  "name": "string",
  "projectId": "string",
  "componentId": "string",
  "branchId": false,
  "configId": "string",
  "configVersion": "string",
  "state": "created",
  "desiredState": "running",
  "lastRequestTimestamp": "string",
  "url": "string",
  "autoSuspendAfterSeconds": 0
}
```

Make note of the `id` field in the response, as you'll need it for subsequent operations.

### Managing the Data App

#### Get the Data App details

Retrieve information about your Data App:

```bash
curl -X GET "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}" \
  -H 'accept: application/json' \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}"
```

#### Start the Data App

Start your Data App when it's in a stopped state:

```bash
curl -X PATCH "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}" \
  -H 'content-type: application/json' \
  -H "x-kbc-manageapitoken: ${KBC_MANAGE_API_TOKEN}" \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}" \
  -d '{"desiredState":"running","lastRequestTimestamp":"1970-01-01T00:00:00.000Z","restartIfRunning":false,"configVersion":"A","updateDependencies":false}'
```

#### Restart the Data App

Restart your Data App (useful after making changes):

```bash
curl -X PATCH "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}" \
  -H 'content-type: application/json' \
  -H "x-kbc-manageapitoken: ${KBC_MANAGE_API_TOKEN}" \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}" \
  -d '{"desiredState":"running","lastRequestTimestamp":"1970-01-01T00:00:00.000Z","restartIfRunning":true,"configVersion":"A","updateDependencies":false}'
```

#### Get the Data App logs

Download the complete logs for your Data App:

```bash
curl -X GET "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}/logs/download" \
  -H 'accept: text/plain' \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}"
```

#### Tail the Data App logs

Stream recent logs using a timestamp in ISO 8601 format:

```bash
curl -X GET "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}/logs/tail?since=2024-11-04T15%3A30%3A04.271025817Z" \
  -H 'accept: text/plain' \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}"
```

#### Delete the Data App

Remove the Data App when it's no longer needed:

```bash
curl -X DELETE "https://data-science.canary-orion.keboola.dev/apps/${KBC_PROJECT_ID}" \
  -H "x-storageapi-token: ${KBC_STORAGE_API_TOKEN}"
```
