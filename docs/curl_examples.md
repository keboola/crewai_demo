# CrewAI Content Orchestrator API - curl Examples

> [!NOTE]
> This document provides examples of how to interact with the CrewAI Content Orchestrator API using curl commands.
> Replace `YOUR_API_ENDPOINT` in all examples with your actual API endpoint (e.g., `http://localhost:8888` or your deployed API URL).

## Table of Contents
- [Health Check](#health-check)
- [Direct Content Generation](#direct-content-generation)
- [HITL Content Generation](#hitl-content-generation)
- [Check Job Status](#check-job-status)
- [Provide Feedback](#provide-feedback)
- [Approve Content](#approve-content)
- [List Jobs](#list-jobs)
- [List Available Crews](#list-available-crews)
- [Delete a Job](#delete-a-job)
- [Example Workflow](#example-workflow)

## Health Check

Check if the API is running:

```bash
curl YOUR_API_ENDPOINT/health
```

## Direct Content Generation

<details>
<summary>Generate content directly without human approval</summary>

```bash
# Asynchronous (non-blocking)
curl -X POST YOUR_API_ENDPOINT/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Artificial Intelligence",
      "require_approval": false
    }
  }'
```

> [!WARNING]
> The `wait=true` parameter is not currently functional. All jobs are processed asynchronously regardless of this setting.

</details>

## HITL Content Generation

<details>
<summary>Generate content with Human-in-the-Loop workflow</summary>

```bash
# Without webhook
curl -X POST YOUR_API_ENDPOINT/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Climate Change",
      "require_approval": true
    }
  }'

# With webhook for notifications
curl -X POST YOUR_API_ENDPOINT/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Climate Change",
      "require_approval": true
    },
    "webhook_url": "http://your-webhook-endpoint.com/webhook"
  }'
```
</details>

## Check Job Status

Check the status of a specific job:

```bash
curl YOUR_API_ENDPOINT/job/YOUR_JOB_ID
```

Replace `YOUR_JOB_ID` with the actual job ID returned from the kickoff request.

## Provide Feedback

<details>
<summary>Provide feedback for a job that's pending approval</summary>

```bash
curl -X POST YOUR_API_ENDPOINT/job/YOUR_JOB_ID/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please make the content more concise and add more examples about renewable energy.",
    "approved": false
  }'
```
</details>

## Approve Content

<details>
<summary>Approve content for a job that's pending approval</summary>

```bash
curl -X POST YOUR_API_ENDPOINT/job/YOUR_JOB_ID/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Content approved as is.",
    "approved": true
  }'
```
</details>

## List Jobs

<details>
<summary>List all jobs (with optional filtering)</summary>

```bash
# List all jobs (limited to 10)
curl YOUR_API_ENDPOINT/jobs

# List jobs with a specific status
curl YOUR_API_ENDPOINT/jobs?status=completed

# List more jobs
curl YOUR_API_ENDPOINT/jobs?limit=20
```
</details>

## List Available Crews

List all available crews in the system:

```bash
curl YOUR_API_ENDPOINT/list-crews
```

## Delete a Job

Delete a specific job:

```bash
curl -X DELETE YOUR_API_ENDPOINT/job/YOUR_JOB_ID
```

## Example Workflow

<details>
<summary>Complete example workflow using curl</summary>

1. Start a HITL job:
```bash
curl -X POST YOUR_API_ENDPOINT/kickoff \
  -H "Content-Type: application/json" \
  -d '{
    "crew": "ContentCreationCrew",
    "inputs": {
      "topic": "Renewable Energy",
      "require_approval": true
    }
  }' | jq
```

2. Save the job ID from the response:
```bash
export JOB_ID="job_id_from_response"
```

3. Check job status until it's pending approval:
```bash
curl YOUR_API_ENDPOINT/job/$JOB_ID | jq
```

4. Provide feedback:
```bash
curl -X POST YOUR_API_ENDPOINT/job/$JOB_ID/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "Please add more examples about solar power.",
    "approved": false
  }' | jq
```

5. Check job status again until it's completed:
```bash
curl YOUR_API_ENDPOINT/job/$JOB_ID | jq
```

> [!TIP]
> The `jq` command is used to format the JSON response. If you don't have it installed, you can omit it.
</details> 