# ADK Patterns

A collection of Google Agent Development Kit (ADK) patterns built with Python and Gemini, organized by architecture type.

## Patterns

### Day 1a — Single Agent
A simple agent with Google Search tool. The foundation of ADK agent development.

### Day 1b — Multi-Agent Architectures
Four patterns for coordinating multiple agents:

- **Orchestrator** — An LLM coordinator that dynamically decides which sub-agents to call and in what order
- **Sequential** — A guaranteed assembly line: Outline → Write → Edit
- **Parallel** — Independent agents running concurrently, results combined by an aggregator
- **Loop** — An iterative refinement cycle: Writer ↔ Critic, until approved or max iterations reached

## Project Structure

```
adk-patterns/
├── day1a/              # Single agent with Google Search
│   └── agent.py
└── day1b/              # Multi-agent patterns
    ├── config.py       # Shared model and retry configuration
    ├── orchestrator/   # LLM-based dynamic orchestration
    ├── sequential/     # Guaranteed ordered pipeline
    ├── parallel/       # Concurrent execution
    └── loop/           # Iterative refinement cycle
```

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install google-adk python-dotenv`
5. Create a `.env` file in the root with your Gemini API key:

```
GOOGLE_API_KEY=your_key_here
```

## Running

```bash
# Single agent
adk web day1a

# Multi-agent patterns (pick from dropdown)
adk web day1b
```

## Requirements
- Python 3.9–3.12
- Gemini API key from [Google AI Studio](https://aistudio.google.com/app/api-keys)