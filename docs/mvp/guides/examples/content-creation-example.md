# Content Creation Example with Human-in-the-Loop

This document provides a detailed walkthrough of testing the AI Agent Platform with a content creation example that demonstrates human-in-the-loop capabilities.

## Overview

The content creation example demonstrates a complete workflow for generating content with human-in-the-loop (HITL) capabilities. It includes:

- A research agent for gathering information
- A writer agent for creating content
- An editor agent for refining content
- Support for human feedback and approval

## Setup

1. **Ensure the environment is properly configured**:

   ```bash
   # Create and activate a virtual environment
   python -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -e ".[dev]"
   uv pip install langchain langchain_openai
   ```

2. **Configure the .env file**:

   ```bash
   # Set the path to your agent file
   AGENT_ENTRYPOINT=examples/your_agent.py
   
   # Configure the LLM provider
   LLM_PROVIDER=openrouter
   OPENAI_API_KEY=your-api-key-here
   OPENAI_API_BASE=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=openai/gpt-4o-mini
   ```

3. **Run the API server**:

   ```bash
   bash scripts/run_api.sh
   ```

## Testing the API

### 1. List Available Crews

First, check if the API can detect your crew:

```bash
curl -s http://localhost:8000/list-crews | jq
```

Expected response:
```json
{
  "crews": [
    "YourCrewName"
  ]
}
```

### 2. Start a Content Creation Job

Start a new job with your crew:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "crew": "YourCrewName",
  "inputs": {
    "topic": "Artificial Intelligence",
    "require_approval": true
  }
}' http://localhost:8000/kickoff | jq
```

Expected response:
```json
{
  "job_id": "ad635474-1850-4b7d-b64b-54effa75563d",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

### 3. Check Job Status

Check the status of the job using the job ID from the previous step:

```bash
curl -s http://localhost:8000/job/ad635474-1850-4b7d-b64b-54effa75563d | jq
```

The job will initially be in the "processing" state. After a few minutes, it should transition to "pending_approval" with the generated content:

```json
{
  "id": "ad635474-1850-4b7d-b64b-54effa75563d",
  "crew": "YourCrewName",
  "inputs": {
    "topic": "Artificial Intelligence"
  },
  "status": "pending_approval",
  "created_at": "2025-03-14T19:51:00.754039",
  "webhook_url": null,
  "result": {
    "status": "needs_approval",
    "content": "# Artificial Intelligence: A Comprehensive Overview\n\n...",
    "length": 6149,
    "timestamp": "2025-03-14T19:52:21.926011"
  }
}
```

### 4. Provide Feedback

Provide feedback on the generated content:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "feedback": "Great content! Please add a section about AI ethics.",
  "approved": false
}' http://localhost:8000/job/ad635474-1850-4b7d-b64b-54effa75563d/feedback | jq
```

Expected response:
```json
{
  "message": "Feedback recorded and content generation restarted with feedback",
  "job_id": "ad635474-1850-4b7d-b64b-54effa75563d"
}
```

### 5. Check Updated Content

Check the job status again to see the updated content:

```bash
curl -s http://localhost:8000/job/ad635474-1850-4b7d-b64b-54effa75563d | jq
```

The job will be in the "pending_approval" state again with updated content that incorporates your feedback.

### 6. Approve the Content

Approve the updated content:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "feedback": "The content looks great with the added section on AI ethics!",
  "approved": true
}' http://localhost:8000/job/ad635474-1850-4b7d-b64b-54effa75563d/feedback | jq
```

Expected response:
```json
{
  "message": "Feedback recorded and job marked as completed",
  "job_id": "ad635474-1850-4b7d-b64b-54effa75563d"
}
```

### 7. Verify Job Completion

Check the job status one more time to confirm it's completed:

```bash
curl -s http://localhost:8000/job/ad635474-1850-4b7d-b64b-54effa75563d | jq
```

Expected response:
```json
{
  "id": "ad635474-1850-4b7d-b64b-54effa75563d",
  "crew": "YourCrewName",
  "inputs": {
    "topic": "Artificial Intelligence",
    "feedback": "Great content! Please add a section about AI ethics."
  },
  "status": "completed",
  "created_at": "2025-03-14T19:51:00.754039",
  "webhook_url": null,
  "result": {
    "status": "needs_approval",
    "content": "# Artificial Intelligence: A Comprehensive Overview\n\n...",
    "length": 6149,
    "timestamp": "2025-03-14T19:52:21.926011"
  },
  "completed_at": "2025-03-14T19:52:52.323539"
}
```

## Troubleshooting

### Module Loading Issues

If you encounter the error `<class 'user_script.YourCrewClass'> is a built-in class`, it's likely due to an issue with how the module is being loaded. The fix is to ensure the module is properly registered in `sys.modules` before execution:

```python
# In src/frameworks/crewai/adapter.py
def load_agent(self, code_path: str) -> Any:
    # ... existing code ...
    
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location("user_script", code_path)
        user_module = importlib.util.module_from_spec(spec)
        # Register the module in sys.modules before executing it
        sys.modules["user_script"] = user_module
        spec.loader.exec_module(user_module)
        
        # ... rest of the method ...
    except Exception as e:
        # ... error handling ...
```

### Missing Dependencies

Make sure you have all the required dependencies installed:

```bash
uv pip install langchain langchain_openai
```

## Conclusion

This content creation example demonstrates the full capabilities of the AI Agent Platform, including:

1. **Multi-agent workflows**: Research, writing, and editing agents working together
2. **Human-in-the-loop (HITL)**: Ability to review and provide feedback on generated content
3. **Feedback incorporation**: Agents can incorporate human feedback to improve the content
4. **Asynchronous execution**: Jobs run in the background and can be monitored via the API
5. **Multiple LLM providers**: Support for OpenRouter, Azure OpenAI, and other providers

This example serves as a template for building your own AI agent workflows with human oversight and feedback mechanisms. 