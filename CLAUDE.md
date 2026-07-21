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

## Planned file structure

```
p01-react-agent/
├── main.py                        # thin entry point only
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── loop.py                # ReAct loop (not yet created)
│       ├── config.py              # pydantic-settings config (working)
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py          # Responses API calls (working, needs prompt param)
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py        # tool discovery + JSON schema (not yet created)
│       │   └── web_search.py      # first real tool (not yet created)
│       └── models/
│           ├── __init__.py
│           ├── messages.py        # Pydantic: Message, ConversationState (not yet created)
│           └── tool_call.py       # Pydantic: ToolCall, ToolResult (not yet created)
├── evals/
│   ├── dataset.json               # 20 Q&A eval pairs (not yet created)
│   ├── metrics.py                 # accuracy, hallucination rate, tool efficiency (not yet created)
│   └── run_evals.py               # eval CLI entrypoint (not yet created)
└── tests/
    ├── conftest.py
    ├── test_loop.py
    └── test_tools.py
```

Build order: config → llm/client → models/messages → loop → tools

---

## Immediate next steps

1. **Add `prompt` parameter to `get_response()`** — replace the hardcoded prompt so the function is reusable
2. **Create `models/messages.py`** — Pydantic models for `Message` and `ConversationState`
3. **Build `loop.py`** — the actual ReAct loop
4. **Create `tools/registry.py`** — tool discovery + JSON schema generation
5. **Create `tools/web_search.py`** — first real tool implementation

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
