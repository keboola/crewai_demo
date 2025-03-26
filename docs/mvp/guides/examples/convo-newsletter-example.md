# ConvoNewsletterOpenRouter Example

This example demonstrates how to use the AI Agent Platform with OpenRouter as the LLM provider to generate newsletters.

## Overview

The ConvoNewsletterOpenRouter example is a CrewAI-based agent that generates newsletters based on a simple brain dump or topic. It uses OpenRouter as the LLM provider, which allows you to access various LLM models through a single API.

The crew consists of three agents:
1. **Newsletter Strategist and Synthesizer**: Creates an outline and subject line based on the input
2. **AI Developer Newsletter Writer**: Writes the newsletter based on the outline
3. **AI Developer Newsletter Editor**: Reviews and finalizes the newsletter

## Setup

### Prerequisites

- An OpenRouter API key (sign up at [OpenRouter](https://openrouter.ai/))
- Python 3.12 or higher
- AI Agent Platform installed

### Configuration

1. Update your `.env` file with the following settings:

```
# LLM Provider Configuration
LLM_PROVIDER=openrouter
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o-mini

# User Code Configuration
AGENT_ENTRYPOINT=examples/convo_newsletter_openrouter/src/convo_newsletter_openrouter/main.py
```

Replace `your-openrouter-api-key` with your actual OpenRouter API key.

## Usage

### Starting the API Server

1. Navigate to the AI Agent Platform directory:
   ```bash
   cd ai-agent-platform
   ```

2. Run the API server:
   ```bash
   bash scripts/run_api.sh
   ```

### Creating a Newsletter

1. Use the `/kickoff` endpoint to start a new job:
   ```bash
   curl -X POST http://localhost:8000/kickoff \
     -H "Content-Type: application/json" \
     -d '{"inputs": {"brain_dump": "I would like to write a newsletter about the challenges of finding AI software jobs and how to stand out by showcasing your work publicly."}}'
   ```

2. The response will include a job ID:
   ```json
   {
     "job_id": "2bd7d60b-790f-4167-b393-91f075b377ca",
     "status": "queued",
     "message": "Crew kickoff started in the background"
   }
   ```

3. Check the job status:
   ```bash
   curl http://localhost:8000/job/2bd7d60b-790f-4167-b393-91f075b377ca
   ```

4. Once the job is complete, the status will change to "pending_approval" and the result will contain the generated newsletter.

5. Approve the job:
   ```bash
   curl -X POST http://localhost:8000/job/2bd7d60b-790f-4167-b393-91f075b377ca/feedback \
     -H "Content-Type: application/json" \
     -d '{"approved": true, "feedback": "Great job! The newsletter looks excellent."}'
   ```

## Customization

### Changing the OpenRouter Model

You can change the OpenRouter model by updating the `OPENROUTER_MODEL` environment variable in your `.env` file. Some available models include:

- `openai/gpt-4o-mini`
- `openai/gpt-4o`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`

For a full list of available models, see the [OpenRouter documentation](https://openrouter.ai/docs).

### Modifying the Newsletter Format

The newsletter format is defined in the task configurations in `examples/convo_newsletter_openrouter/src/convo_newsletter_openrouter/config/tasks.yaml`. You can modify this file to change the structure, tone, or content of the generated newsletters.

## Troubleshooting

### Word Counter Tool Issues

If you encounter issues with the Word Counter Tool, such as infinite loops or repeated error messages, check the following:

1. Make sure you're using the latest version of the tool with the caching mechanism
2. Restart the API server to ensure the changes take effect
3. Check the logs for any error messages

For more details on the Word Counter Tool fix, see [Word Counter Tool Bug Fix](../bug_fixes/word_counter_tool_fix.md). 