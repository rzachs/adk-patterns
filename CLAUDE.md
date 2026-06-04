# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running agents

```bash
# Activate the venv first
venv\Scripts\Activate.ps1

# Launch ADK web UI for a pattern group
adk web day1a
adk web day1b

# Run a specific sub-pattern directly (pick from the dropdown in the web UI after adk web day1b)
```

The `adk web` command serves a local UI where you select the agent to chat with. There is no test suite or build step.

## Environment

Requires a `.env` file in the project root:
```
GOOGLE_API_KEY=your_key_here
```

Get a key from [Google AI Studio](https://aistudio.google.com/app/api-keys). The `.env` is gitignored.

## Architecture

### day1a — single agent
`day1a/agent.py` defines a single `root_agent` (the name ADK looks for) backed by `gemini-2.5-flash` with `google_search` as a tool.

### day1b — multi-agent patterns
Each sub-directory (`orchestrator/`, `sequential/`, `parallel/`, `loop/`) is a self-contained ADK module with its own `agent.py` defining a `root_agent`. All four share `day1b/config.py`.

**`day1b/config.py`** — shared `get_model()` factory defaulting to `gemini-2.5-flash-lite` with retry config. Sub-agents import this instead of constructing `Gemini(...)` directly.

**Inter-agent data passing** uses `output_key` + template variables. An agent sets `output_key="foo"` and a downstream agent references `{foo}` in its `instruction` string. This is ADK's session-state mechanism — no explicit handoff code needed.

**The four patterns:**

| Pattern | ADK class | How it works |
|---|---|---|
| `sequential/` | `SequentialAgent` | Runs sub-agents in guaranteed order (Outline → Write → Edit) |
| `parallel/` | `ParallelAgent` + `SequentialAgent` | Three researchers run concurrently, then a sequential Aggregator combines via `{tech_research}` / `{health_research}` / `{finance_research}` |
| `loop/` | `LoopAgent` + `SequentialAgent` | Writer drafts, then Critic+Refiner loop until `exit_loop()` tool is called or `max_iterations` is hit |
| `orchestrator/` | `Agent` with `AgentTool` | An LLM coordinator wraps sub-agents as tools and decides call order dynamically |

**Loop escape hatch:** `loop/agent.py` uses a `FunctionTool(exit_loop)` that the RefinerAgent must call when the CriticAgent outputs exactly `"APPROVED"`. Without this the loop runs to `max_iterations`.

**Orchestrator vs Sequential:** The orchestrator pattern uses `AgentTool(agent)` to expose sub-agents as callable tools to a coordinating LLM — control flow is decided at inference time. Sequential/Parallel/Loop have deterministic control flow baked into the pipeline structure.

## Common issues
 
- **`adk` not found**: venv not activated — run `.\venv\Scripts\Activate.ps1` first
- **503 errors**: Gemini free tier rate limit hit — wait or switch to `gemini-2.5-flash-lite`
- **`No module named X`**: each agent folder must be self-contained — no cross-folder imports
- **venv broken after folder rename**: delete and recreate venv, reinstall dependencies
