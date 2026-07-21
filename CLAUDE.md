# P01 — ReAct Agent from Scratch

## What this project is

Part of the **Agentic Engineering Bootcamp v2.1** (26 weeks, 21 projects). This is **Project 1, Phase 1: Foundations**.

The goal is to build a ReAct (Reasoning + Acting) agent using **raw API calls only — no agent frameworks**. This is intentional: the purpose is to understand what frameworks abstract away before using them in later projects (LangGraph in P5, OpenAI Agents SDK in P7, etc.).

Deliverable: a tool-calling research agent that searches the web, reads URLs, and synthesizes findings into structured reports. Includes a 20-question evaluation suite measuring answer accuracy, hallucination rate, and tool-call efficiency.

---

## AI Assistant / Tutor Rules

When helping the developer build this codebase, **do NOT write the complete code for them**. Your role is to act as a **Tutor** and **Design Advisor**.

Follow these guidelines:
1. **Explain and Guide**: Explain the design patterns, class interfaces, and concepts. Prompt the user to write specific, incremental parts of the code.
2. **Review and Check**: Ask the user to show their work or run checks. Review their code, point out any bugs, and prompt them again.
3. **Double-Check Practices**: At the start of every new module design or session, you MUST ask the user:
   > *"Is this the latest and best way to do this?"*
   Research and sanity-check the latest APIs (e.g., modern OpenAI Responses API, Pydantic v2 conventions, or ddgs caching support).

---

## Current state

The project has a working config → client → entry point pipeline:

- `main.py` — thin entry point. Imports `get_response` from `agent.llm.client`, calls it in a `main()` function with `__name__` guard.
- `src/agent/config.py` — `pydantic-settings` `Settings` class. Loads `openai_api_key` and `model` from `.env`. Uses Pydantic v2 `model_config` style.
- `src/agent/llm/client.py` — wraps the OpenAI Responses API. Creates an `OpenAI` client using `settings.openai_api_key`, exposes `get_response()`. Prompt is still hardcoded — needs a `prompt` parameter next.
- `src/agent/__init__.py` and `src/agent/llm/__init__.py` exist so the package is importable.
- `pyproject.toml` has `[tool.setuptools.packages.find] where = ["src"]` so `uv run` resolves the `agent` package.
- `.claude/hooks/` — `SessionStart` and `SessionEnd` hooks that auto-update CLAUDE.md via headless `claude -p`.

---

## What was decided / context

### API choice
Using the **OpenAI Responses API** (`client.responses.create()`), not the legacy Chat Completions API. This is the current OpenAI standard as of 2026. The key differences:
- `input=` instead of `messages=[...]`
- `response.output_text` instead of `response.choices[0].message.content`

### Model
`gpt-5.4-mini` for development and testing. Cost-effective, same API shape as `gpt-5.4`.

### Language/toolchain
- Python 3.13 (pinned in `.python-version`)
- `uv` for package management — run everything with `uv run`, never activate venv manually
- `ruff` for linting/formatting (not yet configured, add as dev dependency when ready)

### ReAct loop mental model (confirmed understanding)
The loop works like this:
1. User sends a prompt
2. LLM responds with a **Thought** — reasoning about what it needs
3. LLM decides on an **Action** — which tool to call and with what arguments
4. **Your code** executes the tool and gets a result
5. You append the result as an **Observation** back into the conversation
6. LLM reads the full history and either loops again or produces a **Final Answer**

Key insight: the conversation history IS the memory. Your code drives the loop — it inspects the response, checks if a tool was called or a final answer was given, and decides whether to continue.

The loop logic is split between two actors:
- **LLM** — produces Thoughts, decides which tool to call
- **Your code** (`loop.py`) — detects tool calls, executes them, appends observations, decides when to stop

---

## Completed file structure

├── .agents/
│   └── skills/
│       ├── research-latest/      # Research sanity check skill (completed)
│       └── update-progress/       # Documentation sync skill (completed)
├── .claude/
│   └── skills/
│       ├── research-latest/      # Claude research skill (completed)
│       └── update-progress/       # Claude doc sync skill (completed)
├── main.py                        # CLI entry point
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── loop.py                # ReAct loop (completed)
│       ├── config.py              # pydantic-settings config (working)
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py          # Responses API wrapper (completed)
│       ├── tools/
│       │   ├── __init__.py        # Exports registry & tools (completed)
│       │   ├── registry.py        # dynamic registry & schema parser (completed)
│       │   ├── web_search.py      # DuckDuckGo search tool (completed)
│       │   └── read_url.py        # Webpage markdown reader tool (completed)
│       └── models/
│           ├── __init__.py
│           └── messages.py        # Pydantic models for Message and ConversationState (completed)
├── evals/
│   ├── __init__.py
│   ├── dataset.json               # 20-question evaluation dataset (completed)
│   ├── metrics.py                 # accuracy, hallucination, and efficiency metrics (completed)
│   ├── report.md                  # generated markdown report (completed)
│   └── run_evals.py               # evaluation runner CLI (completed)
└── tests/
    ├── conftest.py
    └── test_loop.py               # offline mock unit tests (completed)
```

---

## Immediate next steps

1. **Project 01 is 100% Completed!** 🚀
   * All registries, tools, unit tests, and LLM-as-a-judge evaluations are working.
2. **Transition to Project 02**:
   * Ready to start **Project 02: Build and Publish an MCP Server and Client** in TypeScript.

---

## Dependencies

```toml
dependencies = [
    "openai>=2.32.0",
    "pydantic>=2.13.2",
    "pydantic-settings>=2.13.1",
    "python-dotenv>=1.2.2",
]
```

Packages to add as needed (do not add before the code that needs them exists):
- `httpx` — async HTTP for tool calls
- `beautifulsoup4` + `markdownify` — URL reader tool
- `tiktoken` — token counting
- `rich` — terminal output
- `pytest` + `pytest-asyncio` + `deepeval` — evaluation suite (dev dependencies)
- `ruff` + `mypy` — linting (dev dependencies)
