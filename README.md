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
- [Testing](#testing)
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
│   ├── orchestrator.py       # Main orchestrator for CrewAI using @CrewBase pattern
│   └── tests/                # Tests for CrewAI app
│
├── api_wrapper/              # API wrapper service
│   ├── api_wrapper.py        # Main API service
│   ├── api_client.py         # Client for the API
│   └── tests/                # Tests for API service
│
├── docs/                     # Documentation
│
├── scripts/                  # Utility scripts
│
├── .env.sample              # Environment variable templates
├── .env.azure.sample
└── requirements.txt         # Project dependencies
```
</details>

## Components

### CrewAI Application

The `crewai_app` directory contains the core CrewAI application, which is responsible for content generation using AI agents. The main components are:

- `orchestrator.py`: The main orchestrator that defines the CrewAI crew, agents, and tasks using the `@CrewBase` decorator pattern. All CrewAI functionality is consolidated in this file.
- `tests/`: Tests for the CrewAI application, including integration tests for different LLM providers.

### API Wrapper

The `api_wrapper` directory contains the API service that wraps the CrewAI application and exposes it via a REST API. The main components are:

- `api_wrapper.py`: The main FastAPI application that provides endpoints for interacting with the CrewAI application.
- `api_client.py`: A client for the API that can be used to interact with the API programmatically.
- `tests/`: Tests for the API service.

### Documentation

The project includes comprehensive documentation in the `docs/` directory:

- [API Wrapper Documentation](docs/api_wrapper_documentation.md) - How to use the API wrapper
- [Azure OpenAI Integration](docs/azure_openai_integration.md) - Using Azure OpenAI with the application
- [HITL Workflow](docs/HITL_WORKFLOW.md) - Human-in-the-Loop workflow guide
- [HITL Implementation](docs/HITL_IMPLEMENTATION.md) - Implementation details for HITL

### Scripts

The `scripts` directory contains utility scripts for working with the application, such as webhook receivers, curl examples, and job checking scripts.

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

## Testing

<details>
<summary>Click to see testing instructions</summary>

To test the CrewAI application with different LLM providers:

```bash
# Test Azure OpenAI
python -m crewai_app.tests.test_azure_openai

# Test OpenRouter
python -m crewai_app.tests.test_openrouter

# Test CrewAI integration
python -m crewai_app.tests.test_crewai_integration
```
</details>

## License

[MIT License](LICENSE)
