# P01 — ReAct Agent from Scratch

## What this project is

Part of the **Agentic Engineering Bootcamp v2.3** (26 weeks, 21 projects). This is **Project 1, Phase 1: Foundations**.

The goal is to build a ReAct (Reasoning + Acting) agent using **raw API calls only — no agent frameworks** (although some libraries are used). This is intentional: the purpose is to understand what frameworks abstract away before using them in later projects (LangGraph in P5, OpenAI Agents SDK in P7, etc.).

Deliverable: a tool-calling research agent that searches the web, reads URLs, and synthesizes findings into structured reports. Includes a 20-question evaluation suite measuring answer accuracy, hallucination rate, and tool-call efficiency.

---

## Current state

The project has a working config → client → entry point pipeline, with a fully tested ReAct loop, a dynamic tool registry, and a live web search capability:

- `main.py` — entry point that accepts an optional CLI argument (`sys.argv[1]`) as the user prompt, with a default fallback. Executes the entire ReAct `run_agent_loop` and prints the final result.
- `src/agent/config.py` — `pydantic-settings` `Settings` class. Loads `openai_api_key` and `model` from `.env`. Uses Pydantic v2 `model_config` style.
- `src/agent/llm/client.py` — wraps the OpenAI Responses API. Exposes `get_response` (string prompts) and `get_chat_response` (handles list of message dicts/tools).
- `src/agent/models/messages.py` — Pydantic models for `TextMessage`, `FunctionCallItem`, `FunctionCallOutputItem`, and `ConversationState` matching the modern Responses API schema.
- `src/agent/loop.py` — Fully implemented ReAct loop with support for tool call execution, multi-turn state accumulation, and observation injection (wired with the real tools registry).
- `src/agent/tools/registry.py` — Complete tool registry module that automatically parses function signatures, generates strict OpenAI-compliant JSON schemas, registers functions via `@tool`, and validates/executes tool calls.
- `src/agent/tools/web_search.py` — First real tool implementation (`web_search`) using `ddgs` (without DHT caching, running in direct HTTPS mode) to return formatted search result listings.
- `tests/test_loop.py` — Complete unit test suite verifying simple chat execution and multi-turn tool calling using mock responses and a mocked offline `DDGS` context manager.
- `tests/conftest.py` — Empty conftest setup for pytest.
- `src/agent/__init__.py`, `src/agent/llm/__init__.py`, `src/agent/models/__init__.py`, and `src/agent/tools/__init__.py` exist so packages are importable (utilizing package-level exports and relative imports).
- `pyproject.toml` has package find rules, and the package has been editably installed using `uv pip install -e .` so that the local package resolves natively inside the `.venv`.
- `.vscode/settings.json` configured with `"python.analysis.extraPaths": ["./src"]` to resolve import errors in VS Code Pylance.
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
├── main.py                        # thin entry point only (working)
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── loop.py                # ReAct loop (completed)
│       ├── config.py              # pydantic-settings config (working)
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py          # Responses API calls (working)
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── registry.py        # tool discovery + JSON schema (completed)
│       │   └── web_search.py      # first real tool (completed)
│       └── models/
│           ├── __init__.py
│           └── messages.py        # Pydantic: Message, ConversationState (completed)
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

1. **Project 01 is 100% Completed!** 🚀
   * All dynamic registries, web search and read URL tools, robust offline unit testing, and custom LLM-as-a-judge evaluation metrics are implemented and verified.
2. **Transition to Project 02**:
   * The next project in the syllabus is **Project 02: Build and Publish an MCP (Model Context Protocol) Server and Client** in TypeScript (Week 3).
   * Prepare to initialize the TypeScript workspace for the MCP project.

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
