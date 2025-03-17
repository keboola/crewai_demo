# CrewAI Content Orchestrator API Wrapper

> [!NOTE]
> This documentation explains how to use the CrewAI Content Orchestrator API Wrapper to expose your CrewAI agents and workflows as a RESTful API.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Integration Guide](#integration-guide)
  - [Code Structure Requirements](#code-structure-requirements)
  - [Environment Configuration](#environment-configuration)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Kickoff Endpoint](#kickoff-endpoint)
  - [Job Status](#job-status)
  - [Feedback Endpoint](#feedback-endpoint)
  - [List Jobs](#list-jobs)
  - [List Crews](#list-crews)
  - [Delete Job](#delete-job)
- [Agent Management Endpoints](#agent-management-endpoints)
  - [Agent Validation](#agent-validation)
  - [Agent Metadata](#agent-metadata)
  - [Git Repository Setup](#git-repository-setup)
  - [Git Repository Refresh](#git-repository-refresh)
  - [Upload Code](#upload-code)
- [Webhook Notifications](#webhook-notifications)
  - [Webhook Events](#webhook-events)
- [Job States](#job-states)
- [Implementation Examples](#implementation-examples)
  - [Basic Content Generation](#basic-content-generation)
  - [Human-in-the-Loop Workflow](#human-in-the-loop-workflow)
- [HITL Workflow Example](#hitl-workflow-example)
- [Environment Variables](#environment-variables)
  - [Required Variables](#required-variables)
  - [LLM Provider Configuration](#llm-provider-configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)
  - [API Server Configuration](#api-server-configuration)
  - [Webhook Configuration](#webhook-configuration)
  - [Job Storage](#job-storage)
- [Security Best Practices](#security-best-practices)
- [Further Resources](#further-resources)

## Overview

The CrewAI Content Orchestrator API Wrapper (`api_wrapper.py`) is a FastAPI service that exposes your CrewAI agents and workflows as a RESTful API. This enables:

- **Asynchronous execution** of CrewAI workflows
- **Human-in-the-Loop (HITL)** approval processes
- **Webhook notifications** for job status updates
- **Job tracking** across multiple concurrent executions
- **Scalable deployment** within the AI Agent Platform
- **Agent validation and metadata inspection**
- **Git integration** for code deployment

## Quick Start

<details>
<summary>Click to expand quick start instructions</summary>

1. **Set up your environment**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy and configure environment variables
   cp .env.sample .env
   # Edit .env with your API keys
   ```

2. **Run the API service**:
   ```bash
   bash scripts/run_api.sh
   # Or directly with uvicorn:
   # uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8888 --timeout-keep-alive 300
   ```

3. **Make a request**:
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

## Integration Guide

### Code Structure Requirements

The API wrapper supports two integration patterns:

#### 1. CrewBase Pattern (Recommended)

<details>
<summary>Click to see CrewBase pattern example</summary>

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain.chat_models import ChatOpenAI
import os

@CrewBase
class MyContentCrew:
    """Content creation crew for generating articles"""
    
    def __init__(self, inputs=None):
        """Initialize with inputs from API"""
        self.inputs = inputs or {}
    
    @agent
    def researcher(self) -> Agent:
        """Define a research agent"""
        return Agent(
            role="Research Specialist",
            goal="Find comprehensive information on the topic",
            backstory="You are an expert researcher with years of experience",
            llm=self._get_llm(),
            verbose=True,
        )
    
    @agent
    def writer(self) -> Agent:
        """Define a writer agent"""
        return Agent(
            role="Content Writer",
            goal="Create engaging and informative content",
            backstory="You are a skilled writer who excels at creating engaging content",
            llm=self._get_llm(),
            verbose=True,
        )
    
    @task
    def research_task(self) -> Task:
        """Define a research task"""
        topic = self.inputs.get("topic", "General Knowledge")
        return Task(
            description=f"Research the topic: {topic}",
            expected_output="A detailed research report",
            agent=self.researcher(),
            human_input=False,
        )
    
    @task
    def writing_task(self) -> Task:
        """Define a writing task"""
        return Task(
            description="Write an engaging article based on the research",
            expected_output="A well-structured article",
            agent=self.writer(),
            context=[self.research_task()],
            human_input=self.inputs.get("require_approval", False),
        )
    
    @crew
    def content_crew(self) -> Crew:
        """Define your crew - this will be discovered by the API wrapper"""
        return Crew(
            agents=[self.researcher(), self.writer()],
            tasks=[self.research_task(), self.writing_task()],
            process=Process.sequential,
            verbose=True,
        )
        
    def _get_llm(self):
        """Configure LLM based on environment variables"""
        llm_provider = os.environ.get("LLM_PROVIDER", "openrouter").lower()
        
        if llm_provider == "openrouter":
            # Use OPENAI_API_KEY for OpenRouter
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY must be set for OpenRouter")
            
            model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.7,
            )
        
        elif llm_provider == "azure":
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            deployment_id = os.environ.get("AZURE_OPENAI_DEPLOYMENT_ID")
            api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
            
            if not all([api_key, endpoint, deployment_id]):
                raise ValueError("Azure OpenAI credentials not properly configured")
            
            return ChatOpenAI(
                deployment_name=deployment_id,
                model_name="gpt-4",
                openai_api_key=api_key,
                openai_api_base=endpoint,
                openai_api_version=api_version,
                openai_api_type="azure",
                temperature=0.7,
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
```
</details>

The API wrapper automatically discovers methods decorated with `@crew` and makes them available as endpoints.

#### 2. Direct Function Pattern

> [!NOTE]
> The Direct Function Pattern is currently experimental and may not be fully supported in all versions of the API wrapper. The CrewBase Pattern is the recommended approach.

<details>
<summary>Click to see Direct Function pattern example (experimental)</summary>

```python
from typing import Dict, Any, Optional
from datetime import datetime

def create_content_with_hitl(
    topic: str, 
    feedback: Optional[str] = None, 
    require_approval: bool = True
) -> Dict[str, Any]:
    """
    Content creation function with human-in-the-loop capability
    
    Args:
        topic: The topic to create content about
        feedback: Optional human feedback for refinement
        require_approval: Whether to require human approval
        
    Returns:
        Dictionary with content and status information
    """
    # Implementation here
    return {
        "status": "needs_approval",  # or "success" or "error"
        "content": "Generated content...",
        "length": 1234,
        "timestamp": datetime.now().isoformat(),
    }
```
</details>

### Environment Configuration

Set the path to your CrewAI code in the `AGENT_ENTRYPOINT` environment variable:

```bash
# In .env file
AGENT_ENTRYPOINT="crewai_app/orchestrator.py"
```

## API Endpoints

### Health Check

**Endpoint**: `GET /health`

Returns the health status of the API.

```bash
curl http://localhost:8888/health
```

<details>
<summary>Click to see response example</summary>

```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T12:34:56.789012",
  "module_loaded": true,
  "active_jobs": 2,
  "version": "0.1.0",
  "environment": "production"
}
```
</details>

### Kickoff Endpoint

**Endpoint**: `POST /kickoff`

Starts a new content generation job.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST http://localhost:8888/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Artificial Intelligence",
      "require_approval": true
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook",
    "wait": false
  }'
```
</details>

**Parameters**:
- `crew` (string): The name of the crew class to use
- `inputs` (object): Input parameters for the crew
- `webhook_url` (string, optional): URL to receive job status updates
- `wait` (boolean, optional): Whether to wait for job completion (default: false)

> [!WARNING]
> The `wait=true` parameter is not currently functional. All jobs are processed asynchronously regardless of this setting.

<details>
<summary>Click to see response examples</summary>

**Response (Asynchronous)**:
```json
{
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

**Response (Synchronous, with wait=true)**:
```json
{
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "completed",
  "result": {
    "content": "Generated content...",
    "length": 1234
  }
}
```
</details>

### Job Status

**Endpoint**: `GET /job/{job_id}`

Retrieves the status and result of a specific job.

```bash
curl http://localhost:8888/job/987ca65a-62cf-4c48-850b-ad0eb3e37393
```

<details>
<summary>Click to see response example</summary>

```json
{
  "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "crew": "ContentCreationCrew",
  "inputs": {
    "topic": "Artificial Intelligence"
  },
  "status": "completed",
  "created_at": "2023-06-15T12:34:56.789012",
  "completed_at": "2023-06-15T12:40:56.789012",
  "result": {
    "content": "Generated content...",
    "length": 1234
  }
}
```
</details>

### Feedback Endpoint

**Endpoint**: `POST /job/{job_id}/feedback`

Provides human feedback for a job that's pending approval.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST http://localhost:8888/job/987ca65a-62cf-4c48-850b-ad0eb3e37393/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please make the content more concise and add more examples.",
    "approved": false
  }'
```
</details>

**Parameters**:
- `feedback` (string): Human feedback on the content
- `approved` (boolean): Whether to approve the content as is

<details>
<summary>Click to see response examples</summary>

**Response (Approved)**:
```json
{
  "message": "Feedback recorded and job marked as completed",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```

**Response (Not Approved)**:
```json
{
  "message": "Feedback recorded and content generation restarted with feedback",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```
</details>

### List Jobs

**Endpoint**: `GET /jobs`

Lists all jobs with optional filtering.

```bash
curl "http://localhost:8888/jobs?limit=5&status=completed"
```

**Query Parameters**:
- `limit` (integer, optional): Maximum number of jobs to return (default: 10)
- `status` (string, optional): Filter jobs by status
- `offset` (integer, optional): Pagination offset for large result sets (default: 0)
- `sort_by` (string, optional): Field to sort by (default: "created_at")
- `sort_order` (string, optional): Sort direction, "asc" or "desc" (default: "desc")

<details>
<summary>Click to see response example</summary>

```json
{
  "jobs": [
    {
      "id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
      "crew": "ContentCreationCrew",
      "status": "completed",
      "created_at": "2023-06-15T12:34:56.789012",
      "completed_at": "2023-06-15T12:40:56.789012"
    },
    {
      "id": "123ab45c-78de-9f01-234g-h5i67j8klmno",
      "crew": "ResearchCrew",
      "status": "completed",
      "created_at": "2023-06-15T11:22:33.444555",
      "completed_at": "2023-06-15T11:30:44.555666"
    }
  ],
  "count": 2,
  "total_jobs": 15,
  "offset": 0,
  "limit": 5
}
```
</details>

### List Crews

**Endpoint**: `GET /list-crews`

Lists all available crews that can be used with the kickoff endpoint.

```bash
curl http://localhost:8888/list-crews
```

<details>
<summary>Click to see response example</summary>

```json
{
  "crews": [
    {
      "name": "ContentCreationCrew",
      "description": "Crew for generating content",
      "parameters": {
        "topic": {
          "type": "string",
          "description": "The topic to create content about",
          "required": true
        },
        "require_approval": {
          "type": "boolean",
          "description": "Whether to require human approval",
          "required": false,
          "default": false
        }
      }
    },
    {
      "name": "content_crew",
      "description": "Alternative content creation crew",
      "parameters": {}
    },
    {
      "name": "content_crew_with_feedback",
      "description": "Content creation with feedback loop",
      "parameters": {
        "feedback": {
          "type": "string",
          "description": "Feedback for content refinement",
          "required": false
        }
      }
    }
  ]
}
```
</details>

### Delete Job

**Endpoint**: `DELETE /job/{job_id}`

Deletes a job and its associated data.

```bash
curl -X DELETE http://localhost:8888/job/987ca65a-62cf-4c48-850b-ad0eb3e37393
```

<details>
<summary>Click to see response example</summary>

```json
{
  "message": "Job deleted successfully",
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393"
}
```
</details>

## Agent Management Endpoints

### Agent Validation

**Endpoint**: `GET /agent/validate`

Validates the agent code loaded from the `AGENT_ENTRYPOINT` environment variable.

```bash
curl http://localhost:8888/agent/validate
```

<details>
<summary>Click to see response example</summary>

```json
{
  "valid": true,
  "module_path": "/app/crewai_app/orchestrator.py",
  "crews": [
    {
      "name": "ContentCreationCrew",
      "method": "content_crew"
    },
    {
      "name": "content_crew_with_feedback",
      "method": "content_crew_with_feedback"
    }
  ],
  "message": "Agent code is valid and ready to use"
}
```

**Response (Invalid)**:
```json
{
  "valid": false,
  "module_path": "/app/crewai_app/orchestrator.py",
  "error": "No CrewBase class found in the module",
  "message": "Agent code validation failed"
}
```
</details>

### Agent Metadata

**Endpoint**: `GET /agent/metadata`

Retrieves metadata about the agent code, including available crews, methods, and parameters.

```bash
curl http://localhost:8888/agent/metadata
```

<details>
<summary>Click to see response example</summary>

```json
{
  "module_path": "/app/crewai_app/orchestrator.py",
  "module_name": "crewai_app.orchestrator",
  "crews": [
    {
      "name": "ContentCreationCrew",
      "class_name": "ContentCreationCrew",
      "method": "content_crew",
      "description": "Content creation crew for generating articles",
      "parameters": {
        "topic": {
          "type": "string",
          "description": "The topic to create content about",
          "required": true
        },
        "require_approval": {
          "type": "boolean",
          "description": "Whether to require human approval",
          "required": false,
          "default": false
        }
      }
    },
    {
      "name": "content_crew_with_feedback",
      "class_name": "ContentCreationCrew",
      "method": "content_crew_with_feedback",
      "description": "Content creation with feedback loop",
      "parameters": {
        "topic": {
          "type": "string",
          "description": "The topic to create content about",
          "required": true
        },
        "feedback": {
          "type": "string",
          "description": "Feedback for content refinement",
          "required": false
        }
      }
    }
  ]
}
```
</details>

### Git Repository Setup

**Endpoint**: `POST /setup-git-repo`

Sets up a Git repository for the agent code.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST http://localhost:8888/setup-git-repo \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/crew-ai-project",
    "branch": "main",
    "auth_type": "token",
    "auth_token": "github_pat_token",
    "sparse_checkout": ["crewai_app/", "requirements.txt"]
  }'
```
</details>

**Parameters**:
- `repo_url` (string): Git repository URL
- `branch` (string, optional): Git branch to clone (default: "main")
- `auth_type` (string, optional): Authentication type (none, token, ssh) (default: "none")
- `auth_token` (string, optional): Authentication token for private repositories
- `ssh_key` (string, optional): SSH key for private repositories
- `sparse_checkout` (array, optional): List of paths to sparse checkout

<details>
<summary>Click to see response example</summary>

```json
{
  "status": "success",
  "destination": "/tmp/external",
  "repo_url": "https://github.com/username/crew-ai-project",
  "branch": "main",
  "message": "Git repository set up successfully"
}
```
</details>

### Git Repository Refresh

**Endpoint**: `POST /refresh-git-repo`

Refreshes a Git repository by pulling the latest changes.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST http://localhost:8888/refresh-git-repo \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/crew-ai-project",
    "branch": "main",
    "force_clean": false
  }'
```
</details>

**Parameters**:
- `repo_url` (string): Git repository URL
- `branch` (string, optional): Git branch to pull (default: "main")
- `auth_type` (string, optional): Authentication type (none, token, ssh) (default: "none")
- `auth_token` (string, optional): Authentication token for private repositories
- `ssh_key` (string, optional): SSH key for private repositories
- `sparse_checkout` (array, optional): List of paths to sparse checkout
- `force_clean` (boolean, optional): Whether to force clean the destination directory (default: false)

<details>
<summary>Click to see response example</summary>

```json
{
  "status": "success",
  "destination": "/tmp/external",
  "repo_url": "https://github.com/username/crew-ai-project",
  "branch": "main",
  "message": "Git repository refreshed successfully"
}
```
</details>

### Upload Code

**Endpoint**: `POST /upload-code`

Uploads code for the agent.

<details>
<summary>Click to see request example</summary>

```bash
curl -X POST http://localhost:8888/upload-code \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./my-agent-code.zip" \
  -F "file_type=zip" \
  -F "module_path=crewai_app"
```
</details>

**Parameters**:
- `file` (file): Uploaded file (ZIP, TAR, or Python file)
- `file_type` (string, optional): Type of the file (auto, zip, tar, directory) (default: "auto")
- `module_path` (string, optional): Path to the module within the extracted files

<details>
<summary>Click to see response example</summary>

```json
{
  "status": "success",
  "destination": "/tmp/external",
  "file_type": "zip",
  "extracted_files": 12,
  "message": "Code uploaded and extracted successfully"
}
```
</details>

## Webhook Notifications

The API wrapper can send webhook notifications to a URL you provide when a job's status changes. This is particularly useful for long-running jobs or implementing asynchronous workflows.

<details>
<summary>Click to see webhook payload example</summary>

```json
{
  "job_id": "987ca65a-62cf-4c48-850b-ad0eb3e37393",
  "status": "completed",
  "crew": "ContentCreationCrew",
  "completed_at": "2023-06-15T12:40:56.789012",
  "result": {
    "content": "Generated content...",
    "length": 1234
  }
}
```
</details>

### Webhook Events

The following events trigger webhook notifications:

1. **Job Completed**: When a job finishes successfully
2. **Job Error**: When a job encounters an error
3. **Pending Approval**: When a job is waiting for human approval
4. **Job Resumed**: When a job resumes after approval

## Job States

A job can be in one of the following states:

- **queued**: Job has been created and is waiting to be processed
- **processing**: Job is currently being processed
- **pending_approval**: Job is waiting for human approval
- **completed**: Job has completed successfully
- **error**: Job encountered an error
- **cancelled**: Job was cancelled by the user

## Implementation Examples

### Basic Content Generation

<details>
<summary>Click to see basic content generation example</summary>

```python
# In orchestrator.py
@CrewBase
class ContentCreationCrew:
    """Content creation crew for generating articles"""
    
    def __init__(self, inputs=None):
        self.inputs = inputs or {}
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            role="Content Writer",
            goal="Create engaging content",
            backstory="You are a skilled writer",
            llm=self._get_llm(),
            verbose=True,
        )
    
    @task
    def writing_task(self) -> Task:
        topic = self.inputs.get("topic", "General Knowledge")
        return Task(
            description=f"Write about {topic}",
            expected_output="A well-structured article",
            agent=self.writer_agent(),
            human_input=False,
        )
    
    @crew
    def content_crew(self) -> Crew:
        return Crew(
            agents=[self.writer_agent()],
            tasks=[self.writing_task()],
            process=Process.sequential,
            verbose=True,
        )
    
    def _get_llm(self):
        # Use OPENAI_API_KEY for OpenRouter
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
        
        return ChatOpenAI(
            model="openai/gpt-4o-mini",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.7,
        )
```
</details>

### Human-in-the-Loop Workflow

<details>
<summary>Click to see HITL workflow implementation example</summary>

```python
# In orchestrator.py
@CrewBase
class ContentCreationCrew:
    # ... other methods ...
    
    @agent
    def editor_agent(self) -> Agent:
        return Agent(
            role="Content Editor",
            goal="Improve content quality",
            backstory="You are an expert editor with attention to detail",
            llm=self._get_llm(),
            verbose=True,
        )
    
    @task
    def editing_with_feedback_task(self) -> Task:
        feedback = self.inputs.get("feedback", "Please improve the content.")
        return Task(
            description=f"Edit the content incorporating this feedback: {feedback}",
            expected_output="A polished article addressing the feedback",
            agent=self.editor_agent(),
            context=[self.writing_task()],
            human_input=False,
        )
    
    @crew
    def content_crew_with_feedback(self) -> Crew:
        return Crew(
            agents=[self.writer_agent(), self.editor_agent()],
            tasks=[self.writing_task(), self.editing_with_feedback_task()],
            process=Process.sequential,
            verbose=True,
        )
```
</details>

## HITL Workflow Example

> [!TIP]
> Human-in-the-Loop (HITL) workflows allow for human feedback and approval during the content generation process.

<details>
<summary>Click to see complete HITL workflow example</summary>

1. **Start a job requiring approval**:
   ```bash
   curl -X POST http://localhost:8888/kickoff \
     -H "Content-Type: application/json" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "topic": "Climate Change",
         "require_approval": true
       }
     }'
   ```

2. **Check job status until it's pending approval**:
   ```bash
   curl http://localhost:8888/job/YOUR_JOB_ID
   ```

3. **Provide feedback or approve**:
   ```bash
   # To approve:
   curl -X POST http://localhost:8888/job/YOUR_JOB_ID/feedback \
     -H "Content-Type: application/json" \
     -d '{
       "feedback": "Content approved as is.",
       "approved": true
     }'
   
   # To request changes:
   curl -X POST http://localhost:8888/job/YOUR_JOB_ID/feedback \
     -H "Content-Type: application/json" \
     -d '{
       "feedback": "Please add more examples about renewable energy.",
       "approved": false
     }'
   ```

4. **If feedback was provided, check status again** until it's "pending_approval" again, then review the updated content.
</details>

## Environment Variables

> [!IMPORTANT]
> Make sure to set all required environment variables before running the API wrapper.

### Required Variables

- `AGENT_ENTRYPOINT`: Path to your CrewAI code file (e.g., `crewai_app/orchestrator.py`)

### LLM Provider Configuration

<details>
<summary>OpenRouter Configuration (Default)</summary>

- `LLM_PROVIDER=openrouter`: Set to use OpenRouter
- `OPENAI_API_KEY`: Your API key for OpenRouter
- `OPENAI_API_BASE=https://openrouter.ai/api/v1`: The OpenRouter API base URL
- `OPENROUTER_MODEL=openai/gpt-4o-mini`: The model to use
</details>

<details>
<summary>Azure OpenAI Configuration</summary>

- `LLM_PROVIDER=azure`: Set to use Azure OpenAI
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_VERSION=2023-05-15`: The API version
- `AZURE_OPENAI_DEPLOYMENT_ID=gpt-35-turbo-0125`: The deployment ID
</details>

<details>
<summary>Anthropic Claude Configuration</summary>

- `LLM_PROVIDER=anthropic`: Set to use Anthropic
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL=claude-3-opus-20240229`: The model to use
</details>

### Git Integration Configuration

```bash
# In .env file
GIT_REPOSITORY_URL=https://github.com/username/crew-ai-project
GIT_BRANCH=main
GIT_AUTH_TYPE=token  # none, token, or ssh
GIT_AUTH_TOKEN=github_pat_token  # for private repositories with token auth
GIT_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...  # for private repositories with SSH auth
GIT_SPARSE_CHECKOUT=crewai_app/ requirements.txt  # space-separated list of paths
```

### Job Storage

```bash
# In .env file
JOB_STORAGE_TYPE=memory  # or 'postgres'
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/ai_agent_platform  # if using postgres
POSTGRES_MIN_CONNECTIONS=1  # if using postgres
POSTGRES_MAX_CONNECTIONS=10  # if using postgres
```

## Troubleshooting

> [!WARNING]
> Common issues you might encounter when using the API wrapper and how to solve them.

<details>
<summary>Module Loading Issues</summary>

**Problem**: API fails to load your module
```
Error: Failed to load user script: No module named 'crewai_app'
```

**Solutions**:
- Verify `AGENT_ENTRYPOINT` is set correctly in your `.env` file
- Ensure the Python path includes your project root
- Check that the file exists and has the correct permissions
- Try using an absolute path to the file
- Use the `/agent/validate` endpoint to check if your code is valid
</details>

<details>
<summary>Crew Discovery Issues</summary>

**Problem**: API can't find your crew
```
Error: Crew ContentCreationCrew not found in user module
```

**Solutions**:
- Ensure your class is decorated with `@CrewBase`
- Check that at least one method is decorated with `@crew`
- Verify the class name matches what you're passing to the API
- Ensure the crew name is exactly as defined in your code (case-sensitive)
- Use the `/list-crews` endpoint to see available crews
- Use the `/agent/metadata` endpoint to get detailed information about crews
</details>

<details>
<summary>API Key Issues</summary>

**Problem**: Authentication errors with LLM providers
```
Error: OPENAI_API_KEY must be set for OpenRouter
```

**Solutions**:
- Set `OPENAI_API_KEY` in your `.env` file
- For Azure, ensure `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are set
- Verify the API keys are valid and have not expired
- Check that the LLM provider is correctly specified in your configuration
</details>

<details>
<summary>Job Execution Issues</summary>

**Problem**: Jobs fail to execute or get stuck
```
Error: 'NoneType' object has no attribute 'kickoff'
```

**Solutions**:
- Check that your crew method returns a valid Crew object
- Ensure all required inputs are provided
- Look for exceptions in your agent or task code
- Verify LLM configuration is correct
- Check log files for detailed error messages
</details>

<details>
<summary>Webhook Issues</summary>

**Problem**: Webhook notifications not being received

**Solutions**:
- Verify the webhook URL is publicly accessible
- Check that your webhook endpoint returns a 200 status code
- Enable webhook retry in your configuration
- Check the logs for webhook delivery attempts
- Test with a simple webhook echo service to verify formatting
</details>

<details>
<summary>Git Repository Issues</summary>

**Problem**: Git repository setup or refresh fails

**Solutions**:
- Verify that the repository URL is correct
- For private repositories, ensure authentication credentials are correct
- Check if the branch exists
- Ensure you have appropriate permissions to access the repository
- For SSH authentication, verify the SSH key format is correct
</details>

## Advanced Configuration

### API Server Configuration

```bash
# In .env file
API_HOST=0.0.0.0
API_PORT=8888
API_WORKERS=1
API_LOG_LEVEL=info
API_REQUEST_TIMEOUT=300  # Timeout in seconds
API_ALLOW_ORIGINS=*  # CORS configuration
```

### Webhook Configuration

```bash
# In .env file
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_RETRY_DELAY=5
WEBHOOK_TIMEOUT=10
WEBHOOK_VERIFY_SSL=true
```

### Job Storage

```bash
# In .env file
JOB_STORAGE_TYPE=memory  # or 'postgres'
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/ai_agent_platform  # if using postgres
POSTGRES_MIN_CONNECTIONS=1  # if using postgres
POSTGRES_MAX_CONNECTIONS=10  # if using postgres
JOB_RETENTION_DAYS=30  # Number of days to keep completed jobs
```

### Performance Tuning

```bash
# In .env file
WORKER_CONCURRENCY=5  # Number of concurrent jobs to process
JOB_QUEUE_MAX_SIZE=100  # Maximum size of the job queue
RESULT_CACHE_SIZE=1000  # Number of job results to cache in memory
```

## Security Best Practices

> [!CAUTION]
> Implementing proper security measures is crucial when deploying to production environments.

When deploying to production:

1. **Use HTTPS** with a valid SSL certificate
2. **Implement authentication** using API keys or OAuth
3. **Restrict CORS** to trusted domains only
4. **Validate webhook URLs** against a whitelist
5. **Set appropriate timeouts** for long-running operations
6. **Monitor and rate limit** requests to prevent abuse
7. **Validate input data** to prevent injection attacks
8. **Use secure environment variables** for sensitive data
9. **Implement proper Git authentication** for private repositories
10. **Validate uploaded code** for security vulnerabilities

## Integration with AI Agent Platform

When deployed as part of the AI Agent Platform, the API wrapper automatically:

1. **Discovers available crews** from your entrypoint file
2. **Exposes RESTful endpoints** for interacting with your agents
3. **Manages job lifecycle** and persistent storage
4. **Provides webhooks** for asynchronous communication
5. **Scales** based on workload requirements
6. **Validates agent code** to ensure it meets requirements
7. **Supports Git integration** for code deployment
