# Human-in-the-Loop (HITL) with CrewAI

> [!NOTE]
> This document provides a comprehensive guide to the Human-in-the-Loop (HITL) functionality in the CrewAI Content Orchestrator, covering both usage instructions and implementation details.

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

1. Start a content generation job
2. Receive a notification when the content is ready for review
3. Review the content and either:
   - Approve it as is
   - Provide feedback for improvements
4. Receive the final content after approval or revision

This approach combines the efficiency of AI-generated content with human oversight and quality control.

## User Guide

This section provides practical instructions for using the HITL functionality.

### Setup

#### 1. Start the API Wrapper Service

First, make sure the API wrapper service is running:

```bash
# Using the provided script
bash scripts/run_api.sh

# Or directly with uvicorn
uvicorn api_wrapper.api_wrapper:app --host 0.0.0.0 --port 8888 --timeout-keep-alive 300
```

#### 2. Start the Webhook Receiver

In a separate terminal, start the webhook receiver:

```bash
python scripts/webhook_receiver.py --host 0.0.0.0 --port 8889
```

This will start a simple webhook receiver that listens for notifications from the API wrapper service. The webhook URL will be `http://localhost:8889/webhook`.

### Using the HITL Workflow

#### Starting a New Job

To start a new content generation job with HITL:

```bash
# Using the provided script
bash scripts/hitl_mode_example.sh "Quantum Computing"

# Or directly with curl
curl -X POST http://localhost:8888/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Quantum Computing",
      "require_approval": true
    },
    "webhook_url": "http://localhost:8889/webhook"
  }'
```

This command:
- Starts a new content generation job on the topic "Quantum Computing"
- Uses the HITL workflow (requires human approval)
- Sends webhook notifications to the webhook receiver

The output will include a job ID that you can use to check the status or provide feedback later.

#### Monitoring Job Status

You can monitor the job status in several ways:

1. **Webhook Receiver**: The webhook receiver will display notifications when:
   - The job is created
   - The job requires approval
   - The job is completed
   - Any errors occur

2. **API Endpoint**: You can check the job status directly:
   ```bash
   curl http://localhost:8888/job/{job_id}
   ```

#### Providing Feedback or Approval

When the job reaches the "pending_approval" state, you can either approve the content or provide feedback:

##### Approving Content

```bash
# Using the API client
python api_wrapper/api_client.py --job-id "your-job-id" --approve

# Or directly with curl
curl -X POST http://localhost:8888/job/your-job-id/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Content approved as is.",
    "approved": true
  }'
```

This will approve the content as is, and the job will be marked as completed.

##### Providing Feedback

```bash
# Using the API client
python api_wrapper/api_client.py --job-id "your-job-id" --feedback "Please add more examples of practical applications of quantum computing"

# Or directly with curl
curl -X POST http://localhost:8888/job/your-job-id/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please add more examples of practical applications of quantum computing",
    "approved": false
  }'
```

This will send your feedback to the API wrapper service, which will then revise the content based on your feedback.

### Workflow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  api_client │────▶│ api_wrapper │────▶│ CrewAI      │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   │                   │
       │                   ▼                   │
       │           ┌─────────────┐            │
       │           │             │            │
       └──────────▶│  webhook    │◀───────────┘
                   │  receiver   │
                   │             │
                   └─────────────┘
```

### Best Practices

1. **Always Use Webhooks**: For HITL workflows, it's best to use webhooks instead of polling. This allows you to:
   - Start multiple jobs concurrently
   - Receive notifications when jobs require attention
   - Avoid unnecessary polling requests

2. **Provide Specific Feedback**: When providing feedback, be as specific as possible to get the best results.

3. **Use Async Mode for Efficiency**: For better performance, use the asynchronous mode when starting jobs.

### Troubleshooting

#### Job Stuck in Processing

If a job seems stuck in the "processing" state for too long:

1. Check the API wrapper logs for errors
2. Verify that the CrewAI service is running correctly
3. Restart the API wrapper service if necessary

#### Webhook Notifications Not Received

If you're not receiving webhook notifications:

1. Make sure the webhook receiver is running
2. Check that the webhook URL is correct
3. Verify that there are no network issues between the API wrapper and webhook receiver

#### Invalid Job ID

If you get an error about an invalid job ID:

1. Make sure you're using the correct job ID
2. Check if the job has expired (jobs are stored in memory and may be lost if the service restarts)

### Example Workflow

<details>
<summary>Click to see a complete example workflow</summary>

1. Start the webhook receiver:
   ```bash
   python scripts/webhook_receiver.py
   ```

2. Start a new job:
   ```bash
   bash scripts/hitl_mode_example.sh "Artificial Intelligence Ethics"
   ```

3. Wait for the webhook notification that the job requires approval

4. Provide feedback:
   ```bash
   curl -X POST http://localhost:8888/job/your-job-id/feedback \
     -H "Content-Type: application/json" \
     -d '{
       "feedback": "Please focus more on the ethical implications for privacy",
       "approved": false
     }'
   ```

5. Wait for the webhook notification that the job is completed

6. View the final content:
   ```bash
   curl http://localhost:8888/job/your-job-id
   ```
</details>

## Implementation Guide

This section provides technical details about how the HITL functionality is implemented.

### Components

1. **`crewai_app/orchestrator.py`**
   - Implemented using CrewAI's `@CrewBase` decorator pattern
   - Defined agents with `@agent` annotation for research, writing, and editing
   - Created tasks with `@task` annotation for each step of the content creation process
   - Configured crews with `@crew` annotation for standard and feedback-based workflows
   - Returns appropriate status codes to indicate when human approval is needed

2. **`api_wrapper/api_wrapper.py`**
   - Provides a RESTful API wrapper around CrewAI functionality
   - Exposes `/kickoff` endpoint to start crew execution asynchronously
   - Enhanced background job processing to detect "needs_approval" status
   - Improved feedback endpoint to handle approval and rejection
   - Added webhook notifications for all stages of the HITL process
   - Implemented job retry with feedback when content is not approved

3. **`api_wrapper/api_client.py`**
   - Client library for interacting with the API
   - Supports providing feedback or approving content
   - Includes webhook URL configuration for notifications

4. **`scripts/webhook_receiver.py`**
   - Simple webhook receiver for testing webhook notifications
   - Stores and displays received webhook data

### Technical Workflow

<details>
<summary>Click to see the detailed technical workflow</summary>

1. **Content Creation Request**
   - Client calls `/kickoff` with the `ContentCreationCrew` crew
   - System starts processing the request asynchronously
   - Returns a job ID immediately

2. **Initial Content Generation**
   - CrewAI agents (research, writer, editor) generate content
   - When complete, job status is set to "pending_approval"
   - Webhook notification is sent if URL was provided

3. **Human Review**
   - Human reviews the content and decides to approve or provide feedback
   - Feedback is submitted via the `/job/{job_id}/feedback` endpoint

4. **Feedback Processing**
   - If approved, job is marked as completed
   - If not approved, content is regenerated with the feedback using a specialized crew
   - Webhook notification is sent about the job status change
</details>

### Implementation Details

The HITL workflow is implemented through a combination of CrewAI's task system and the API wrapper's job management. Key implementation details include:

1. **Approval Flag**
   - The `require_approval` flag in the input parameters determines if human approval is needed
   - When set to `true`, the job will pause at the appropriate point for human review

2. **Status Management**
   - The API wrapper tracks job status through a state machine
   - The "pending_approval" state indicates that human input is required
   - Webhook notifications are sent on state transitions

3. **Feedback Loop**
   - When feedback is provided, it's passed back to the CrewAI workflow
   - A specialized crew is used to incorporate the feedback and generate revised content
   - The process can repeat until the content is approved

### CrewAI Integration

<details>
<summary>Click to see CrewAI integration details</summary>

The implementation follows CrewAI's recommended patterns:

1. **Class-Based Structure**
   - Uses `@CrewBase` decorator for the main class
   - Organizes agents, tasks, and crews as methods with appropriate annotations

2. **Agent Configuration**
   - Defines specialized agents with clear roles, goals, and backstories
   - Configures appropriate tools for each agent

3. **Task Definition**
   - Creates tasks with clear descriptions and expected outputs
   - Establishes context relationships between tasks

4. **Crew Orchestration**
   - Sets up sequential process for task execution
   - Configures different crews for different scenarios (with/without feedback)
</details>

### Future Improvements

<details>
<summary>Click to see potential future improvements</summary>

Potential enhancements to consider:

1. **Persistent Storage**: Implement persistent storage for jobs (currently in-memory only)
2. **Multiple Feedback Rounds**: Support multiple rounds of feedback for iterative improvement
3. **Advanced Feedback Handling**: More sophisticated parsing and application of feedback
4. **User Authentication**: Add authentication for the API to secure access
5. **Management Dashboard**: Create a dashboard for managing HITL workflows
6. **Enhanced Memory**: Integration with CrewAI's memory and knowledge features
</details> 