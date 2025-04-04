# 🤖 AI Agent Platform: Human-in-the-Loop (HITL) Workflow

> [!NOTE]
> This document provides a comprehensive guide to the Human-in-the-Loop (HITL) functionality in the AI Agent Platform, covering both usage instructions and implementation details.

## Table of Contents

- [Overview](#overview)
- [User Guide](#user-guide)
  - [Setup](#setup)
  - [Using the HITL Workflow](#using-the-hitl-workflow)
  - [Workflow Diagram](#workflow-diagram)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
  - [Example Workflow](#example-workflow)
- [Implementation Guide](#implementation-guide)
  - [Components](#components)
  - [Technical Workflow](#technical-workflow)
  - [Implementation Details](#implementation-details)
  - [CrewAI Integration](#crewai-integration)
  - [Future Improvements](#future-improvements)

## Overview

The Human-in-the-Loop (HITL) workflow allows you to:

1. Create and deploy CrewAI agents with tasks marked as `human_input=True`
2. Start a run with a webhook URL for notifications
3. Receive a notification when a task pauses for human input
4. Review the task output and either:
   - Approve it to continue execution (equivalent to pressing Enter)
   - Provide feedback to restart the task with your guidance
5. Receive the final output after all tasks complete

This approach integrates smoothly with CrewAI's built-in HITL capabilities.

## User Guide

This section provides practical instructions for using the HITL functionality.

### Setup

#### 1. Configure Your CrewAI Tasks with HITL

When creating your CrewAI agents, mark tasks that need human review with `human_input=True`:

```python
from crewai import Agent, Task, Crew

# Define your agents
researcher = Agent(
    role="Research Analyst",
    goal="Conduct thorough research on topics",
    backstory="You are an expert researcher with a talent for finding information.",
    verbose=True
)

# Define tasks with human input enabled
writing_task = Task(
    description="Create a blog post about AI trends and check with the human before finalizing.",
    agent=researcher,
    expected_output="A polished blog post about AI trends",
    human_input=True  # Enable HITL for this task
)

# Create crew
crew = Crew(
    agents=[researcher],
    tasks=[writing_task],
    verbose=True
)
```

#### 2. Deploy Your CrewAI Agent to the AI Agent Platform

Follow the steps in the [Quickstart Guide](../quickstart.md) to deploy your agent to the platform.

### Using the HITL Workflow

#### Starting a New Run

Start a run with a webhook URL to receive notifications:

```bash
# Using curl
curl -X POST "https://your-runtime-url.agentic.canary-orion.keboola.dev/kickoff" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Quantum Computing"
    },
    "webhook_url": "https://your-webhook-endpoint.com/webhook"
  }'
```

This command:

- Starts a new run for the specified crew
- Provides input parameters (in this case, the topic)
- Configures a webhook URL to receive notifications about run status changes

The response will include a run ID that you can use to track the run:

```json
{
  "run_id": "a8c753f9-00e9-4888-aaf7-762bb10994b5",
  "status": "queued",
  "message": "Crew kickoff started in the background"
}
```

#### Monitoring Run Status

You can monitor the run status in two ways:

1. **Webhook Notifications**: Your webhook endpoint will receive events when:
   - The run is created (`run_RunStatus.QUEUED`)
   - The run starts processing (`run_RunStatus.PROCESSING`)
   - The run pauses for human input (`run_human_input_required`)
   - The run completes (`run_RunStatus.COMPLETED`)
   - The run encounters an error (`run_RunStatus.ERROR`)

2. **API Endpoint**: You can check the run status directly:

   ```bash
   curl "https://your-runtime-url.agentic.canary-orion.keboola.dev/runs/a8c753f9-00e9-4888-aaf7-762bb10994b5" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN"
   ```

   When a run is waiting for human input, the response will include:

   ```json
   {
     "id": "a8c753f9-00e9-4888-aaf7-762bb10994b5",
     "status": "PENDING_HUMAN_INPUT",
     "crew": "ContentCreationCrew",
     "inputs": { "topic": "Quantum Computing" },
     "result": null,
     "created_at": "2025-04-03T21:14:23Z",
     "started_at": "2025-04-03T21:14:23Z",
     "completed_at": null,
     "error": null,
     "webhook_url": "https://your-webhook-endpoint.com/webhook",
     "hitl_context": {
       "interaction_type": "input",
       "task_id": "crew_ContentCreationCrew",
       "prompt": "<The prompt shown to the user>",
       "task_output": "<The output of the task that triggered the pause>",
       "created_at": "2025-04-03T21:14:42Z"
     },
     "hitl_history": []
   }
   ```

#### Providing Input or Feedback

When you receive a webhook notification with `event: run_human_input_required` or see a run with status `PENDING_HUMAN_INPUT`, you can provide input via the API:

##### To Approve and Continue (Like Pressing Enter)

```bash
curl -X POST "https://your-runtime-url.agentic.canary-orion.keboola.dev/runs/a8c753f9-00e9-4888-aaf7-762bb10994b5/input" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "approve": true
  }'
```

This will send an empty string to the paused `input()` call, allowing the task to continue execution as if the user pressed Enter.

##### To Provide Feedback (Causing Task to Restart)

```bash
curl -X POST "https://your-runtime-url.agentic.canary-orion.keboola.dev/runs/a8c753f9-00e9-4888-aaf7-762bb10994b5/input" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "approve": false,
    "feedback": "The section on quantum entanglement needs more explanation for beginners."
  }'
```

This will send your feedback to the paused `input()` call, causing CrewAI to restart the task with your feedback incorporated, following CrewAI's standard HITL behavior.

### Workflow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  Your App   │────▶│ AI Agent    │────▶│ CrewAI      │
│             │     │ Platform    │     │ (with HITL) │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       │                   ▼                   │
       │           ┌─────────────┐            │
       │           │             │            │
       └──────────▶│  Webhook    │◀───────────┘
                   │  Receiver   │
                   │             │
                   └─────────────┘
```

### Best Practices

1. **Always Use Webhooks**: For HITL workflows, using webhooks is highly recommended as it allows you to:
   - Receive timely notifications when human input is needed
   - Avoid unnecessary polling
   - Build event-driven architectures

2. **Provide Clear Feedback**: When providing feedback, be as specific and clear as possible to guide the agent effectively.

3. **Consider Timeout Handling**: HITL requests have a default timeout of 1 hour. Ensure your system can handle situations where feedback might not be provided within this timeframe.

4. **Track HITL History**: The platform records all HITL interactions in the `hitl_history` field, allowing you to review the conversation history later.

### Troubleshooting

#### Run Not Pausing for Input

If your run isn't pausing for human input:

1. Verify that you've set `human_input=True` on the task
2. Check the logs to see if there are any errors
3. Make sure your CrewAI version is compatible with the platform

#### Webhook Notifications Not Received

If you're not receiving webhook notifications:

1. Verify that your webhook URL is correct and accessible
2. Check that your webhook endpoint is returning a 2xx response
3. Look for any network connectivity issues

#### Input Not Processing

If providing input doesn't resume the run:

1. Check that the run is still in the `PENDING_HUMAN_INPUT` state
2. Verify that your JSON payload format is correct
3. Try providing input again after a short delay

### Example Workflow

<details>
<summary>Click to see a complete example workflow</summary>

1. Deploy a CrewAI agent with HITL enabled:

   ```bash
   # See the Quickstart Guide for deployment steps
   ```

2. Start a new run:

   ```bash
   curl -X POST "https://your-runtime-url.agentic.canary-orion.keboola.dev/kickoff" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "crew": "ContentCreationCrew",
       "inputs": {
         "topic": "Artificial Intelligence Ethics"
       },
       "webhook_url": "https://your-webhook-endpoint.com/webhook"
     }'
   ```

3. Receive webhook notification when input is required:

   ```json
   {
     "run_id": "a8c753f9-00e9-4888-aaf7-762bb10994b5",
     "task_id": "crew_ContentCreationCrew",
     "status": "PENDING_HUMAN_INPUT",
     "prompt": "Please review this draft on AI Ethics and provide feedback:\n\nArtificial Intelligence Ethics...[content]",
     "task_output": "Artificial Intelligence Ethics...[content]",
     "event": "run_human_input_required"
   }
   ```

4. Provide feedback:

   ```bash
   curl -X POST "https://your-runtime-url.agentic.canary-orion.keboola.dev/runs/a8c753f9-00e9-4888-aaf7-762bb10994b5/input" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
     -d '{
       "approve": false,
       "feedback": "Please focus more on the ethical implications for privacy and add a section on regulation."
     }'
   ```

5. Receive webhook notification when run completes:

   ```json
   {
     "run_id": "a8c753f9-00e9-4888-aaf7-762bb10994b5",
     "status": "COMPLETED",
     "event": "run_RunStatus.COMPLETED"
   }
   ```

6. View the final result:

   ```bash
   curl "https://your-runtime-url.agentic.canary-orion.keboola.dev/runs/a8c753f9-00e9-4888-aaf7-762bb10994b5" \
     -H "Authorization: Bearer YOUR_AUTH_TOKEN"
   ```

</details>

## Implementation Guide

This section provides technical details about how the HITL functionality is implemented in the AI Agent Platform.

### Components

The HITL implementation consists of several key components:

1. **HITL Module (`runtime/hitl/`)**:
   - `models.py`: Defines data models for HITL interactions
   - `monkey_patch.py`: Intercepts CrewAI's `input()` function calls
   - `utils.py`: Utilities for managing HITL workflows

2. **Run Status Management**:
   - The `RunStatus` enum includes `PENDING_HUMAN_INPUT` for runs waiting for input
   - The `Run` model includes `hitl_context` and `hitl_history` fields

3. **API Endpoints**:
   - `/runs/{run_id}/input`: Endpoint for providing input to paused runs

4. **CrewAI Integration**:
   - The CrewAI adapter applies the monkey patch
   - Run context is maintained during execution

### Technical Workflow

1. **HITL Initialization**:
   - The monkey patch replaces Python's built-in `input()` function
   - When a run starts, HITL context is established

2. **Task Execution and Pause**:
   - When a task with `human_input=True` calls `input()`, the monkey-patched function intercepts it
   - The run status is changed to `PENDING_HUMAN_INPUT`
   - A webhook notification is sent
   - The execution thread waits for input

3. **Input Processing**:
   - When input is received via the API, it's passed to the waiting thread
   - Based on the `approve` flag, either an empty string or the feedback is provided
   - The run status is changed back to `PROCESSING`

4. **Execution Continuation**:
   - If approved, the task continues execution
   - If feedback was provided, CrewAI restarts the task with the feedback incorporated

### Implementation Details

The implementation follows these principles:

1. **Non-Intrusive**: The HITL functionality is implemented as a monkey patch, requiring no changes to user code.
2. **Standard-Compliant**: The implementation follows CrewAI's standard HITL behavior.
3. **Reliable**: Thread synchronization ensures that runs pause and resume correctly.
4. **Traceable**: All HITL interactions are recorded in the run history.

### CrewAI Integration

The integration with CrewAI leverages CrewAI's built-in HITL capabilities:

1. **Task Configuration**: Users mark tasks with `human_input=True`
2. **Input Interception**: The platform intercepts `input()` calls
3. **Task Restart**: When feedback is provided, CrewAI restarts the task internally

### Future Improvements

Potential future improvements to the HITL functionality include:

1. **Interactive UI**: A web interface for reviewing and providing input
2. **Multiple Input Types**: Support for different types of input (text, choice, file)
3. **Conditional HITL**: Enable/disable HITL based on runtime conditions
4. **Batch Processing**: Ability to provide input for multiple runs at once
5. **Automated Testing**: Comprehensive testing infrastructure for HITL workflows

---

**Last Updated:** April 4, 2024
