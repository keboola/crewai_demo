# CrewAI Demo

> [!NOTE]
> This repository contains a demo of using CrewAI for content generation with human-in-the-loop capabilities, along with an API wrapper to serve the CrewAI application.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Components](#components)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [LLM Provider Support](#llm-provider-support)
- [Generic API Wrapper](#generic-api-wrapper)
- [Human-in-the-Loop (HITL)](#human-in-the-loop-hitl)
- [Environment Variable Handling](#environment-variable-handling)
- [License](#license)

## Overview

This project demonstrates how to build AI agent workflows using the CrewAI framework and expose them as a RESTful API. Key features include:

- **Human-in-the-Loop (HITL)** approval processes
- **Asynchronous execution** of AI agent workflows
- **Webhook notifications** for job status updates
- **Support for multiple LLM providers** (OpenRouter, Azure OpenAI)

## Project Structure

<details>
<summary>Click to see the project structure</summary>

```
crewai_demo/                  # Root project directory
│
├── crewai_app/               # CrewAI application
│   ├── __init__.py           # Package initialization
│   └── orchestrator.py       # Main orchestrator for CrewAI using @CrewBase pattern
│
├── api_wrapper/              # API wrapper service
│   ├── __init__.py           # Package initialization
│   ├── api_wrapper.py        # Main API service
│   └── api_client.py         # Client for the API
│
├── docs/                     # Documentation
│   ├── api_wrapper_documentation.md
│   ├── generic_api_wrapper.md
│   ├── azure_openai_integration.md
│   ├── HITL_WORKFLOW.md
│   ├── HITL_IMPLEMENTATION.md
│   └── curl_examples.md
│
├── scripts/                  # Utility scripts
│   ├── run_api.sh            # Script to run the API service
│   ├── check_jobs.sh         # Script to check job status
│   ├── curl_workflow.sh      # Example curl commands for workflows
│   ├── direct_mode_example.sh # Example for direct mode
│   ├── hitl_mode_example.sh  # Example for HITL mode
│   └── webhook_receiver.py   # Simple webhook receiver for testing
│
├── .env.sample              # Environment variable template
├── .env.azure.sample        # Azure-specific environment template
└── requirements.txt         # Project dependencies
```

</details>

## Components

### CrewAI Application

The `crewai_app` directory contains the core CrewAI application, which is responsible for content generation using AI agents. The main component is:

- `orchestrator.py`: The main orchestrator that defines the CrewAI crew, agents, and tasks using the `@CrewBase` decorator pattern. All CrewAI functionality is consolidated in this file.

### API Wrapper

The `api_wrapper` directory contains the API service that wraps the CrewAI application and exposes it via a REST API. The main components are:

- `api_wrapper.py`: The main FastAPI application that provides endpoints for interacting with the CrewAI application.
- `api_client.py`: A client for the API that can be used to interact with the API programmatically.

### Documentation

The project includes comprehensive documentation in the `docs/` directory:

- [API Wrapper Documentation](docs/api_wrapper_documentation.md) - How to use the API wrapper
- [Generic API Wrapper Documentation](docs/generic_api_wrapper.md) - How to use the generic API wrapper with any CrewAI implementation
- [Azure OpenAI Integration](docs/azure_openai_integration.md) - Using Azure OpenAI with the application
- [HITL Workflow](docs/HITL_WORKFLOW.md) - Human-in-the-Loop workflow guide
- [HITL Implementation](docs/HITL_IMPLEMENTATION.md) - Implementation details for HITL
- [cURL Examples](docs/curl_examples.md) - Example API requests using curl

### Scripts

The `scripts` directory contains utility scripts for working with the application:

- `run_api.sh` - Script to start the API server
- `check_jobs.sh` - Script to check the status of jobs
- `curl_workflow.sh` - Example workflow using curl commands
- `direct_mode_example.sh` - Example of using direct mode
- `hitl_mode_example.sh` - Example of using HITL mode
- `webhook_receiver.py` - Simple webhook receiver for testing notifications

## Getting Started

<details>
<summary>Click to expand setup instructions</summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/crewai_demo.git
   cd crewai_demo
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.sample .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the API wrapper**

   ```bash
   bash scripts/run_api.sh
   # Or directly with uvicorn:
   # uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8888 --reload
   ```

5. **Make a test request**

   ```bash
   curl -X POST http://localhost:8888/kickoff \
     -H "Content-Type: application/json" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "topic": "Artificial Intelligence"
       }
     }'
   ```

   For more examples, see the scripts in the `scripts/` directory or the [cURL Examples](docs/curl_examples.md) documentation.

</details>

## LLM Provider Support

> [!IMPORTANT]
> The application supports multiple LLM providers. Make sure to configure the appropriate environment variables.

<details>
<summary>OpenRouter Configuration (Default)</summary>

```bash
# In .env file
LLM_PROVIDER=openrouter
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini
```

Note: OpenRouter uses the `OPENAI_API_KEY` environment variable for authentication.
</details>

<details>
<summary>Azure OpenAI Configuration</summary>

```bash
# In .env file
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_DEPLOYMENT_ID=gpt-35-turbo-0125
```

</details>

See the [Azure OpenAI Integration](docs/azure_openai_integration.md) documentation for more details.

## Generic API Wrapper

The API wrapper has been updated to work with any CrewAI implementation, not just the ContentCreationCrew. It can now handle different crew implementations with different initialization patterns and kickoff methods.

### Key Features

- **Flexible Path Handling**: Automatically adds necessary directories to the Python path to handle various project structures.
- **Dynamic Crew Initialization**: Tries different initialization patterns to accommodate various crew implementations.
- **Adaptive Kickoff Method**: Supports both crews that accept inputs in the kickoff method and those that don't.
- **CrewBase Support**: Works with crews implemented using the CrewBase decorator pattern.
- **Environment Variable Support**: Loads environment variables from `.env` files and allows setting them via the API.

### Using the Generic API Wrapper

To use the generic API wrapper with your own CrewAI implementation:

1. Set the `DATA_APP_ENTRYPOINT` environment variable to point to your main script:

```bash
export DATA_APP_ENTRYPOINT="path/to/your/main.py"
```

2. Make sure any required environment variables are set in your `.env` file:

```bash
# For ConvoNewsletterCrew
ANTHROPIC_API_KEY=your_anthropic_api_key

# For other crews
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
```

3. Start the API server:

```bash
uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8000
```

Or use the provided script:

```bash
./scripts/test_api_wrapper.sh path/to/your/main.py
```

4. Test the API with curl commands:

```bash
./scripts/test_api_curl.sh YourCrewName
```

### Example API Requests

```bash
# Kickoff a job
curl -X POST http://localhost:8000/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "YourCrewName",
    "inputs": {
      "your_input_key": "your_input_value"
    },
    "env_vars": {
      "ANTHROPIC_API_KEY": "your_anthropic_api_key"
    }
  }'

# Check job status
curl -X GET http://localhost:8000/job/{job_id}

# List all jobs
curl -X GET http://localhost:8000/jobs

# List available crews
curl -X GET http://localhost:8000/list-crews
```

## Human-in-the-Loop (HITL)

The project includes a human-in-the-loop (HITL) workflow implementation. Key features include:

- **Approval Process**: Users can approve or reject tasks in the workflow.
- **Task Assignment**: Tasks are assigned to users based on their role in the workflow.
- **Task Completion**: Tasks are marked as completed once they are approved.

## Environment Variable Handling

The API wrapper supports multiple ways to provide environment variables to your CrewAI implementation:

1. **OS Environment Variables**: Set variables in your shell before starting the API server
   ```bash
   export ANTHROPIC_API_KEY=your_api_key
   export EXA_API_KEY=your_exa_api_key
   export MODEL=your_model_name
   ```

2. **`.env` File**: Place a `.env` file in the project root with your environment variables
   ```
   ANTHROPIC_API_KEY=your_api_key
   EXA_API_KEY=your_exa_api_key
   MODEL=your_model_name
   ```

3. **`.streamlit/secrets.toml`**: Use Streamlit's secrets management
   ```toml
   ANTHROPIC_API_KEY = "your_api_key"
   EXA_API_KEY = "your_exa_api_key"
   MODEL = "your_model_name"
   ```

4. **API Request**: Pass environment variables in the request body when calling the `/kickoff` endpoint
   ```json
   {
     "crew": "ConvoNewsletterCrew",
     "inputs": {
       "brain_dump": "Your brain dump content"
     },
     "env_vars": {
       "ANTHROPIC_API_KEY": "your_api_key",
       "EXA_API_KEY": "your_exa_api_key",
       "MODEL": "your_model_name"
     }
   }
   ```

The API wrapper automatically loads variables from `.env` and `.streamlit/secrets.toml` files at startup, making it easy to configure your application without modifying code.

## License

[MIT License](LICENSE)
