# CrewAI Content Creation Demo

This project demonstrates the use of CrewAI framework to create an automated content creation pipeline using multiple AI agents working together.

## Project Structure

```
.
├── agents/
│   ├── research_agent.py   # Research analyst agent
│   ├── writer_agent.py     # Content writer agent
│   └── editor_agent.py     # Content editor agent
├── tasks/
│   └── content_tasks.py    # Task definitions
├── content_creation_crew.py # Main script
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (not tracked in git)
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/padak/crewai_demo.git
cd crewai_demo
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

## Usage

Run the content creation pipeline:
```bash
python content_creation_crew.py
```

## How it Works

The project uses three AI agents working together:

1. **Research Agent**: Gathers and analyzes information on the given topic
2. **Writer Agent**: Creates engaging content based on the research
3. **Editor Agent**: Reviews and optimizes the content

Each agent has specific tasks and works sequentially to produce the final content. 