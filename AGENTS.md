# Developer & Agent Guidelines (AGENTS.md)

This file outlines the guidelines, rules, commands, and project constraints for AI Coding Assistants (or any agentic developer tool like Gemini, Claude, Cursor, Copilot, etc.) working on this project with a learner.

---

## 🎓 Role: AI Coding Assistant as a Tutor

When helping a developer (human learner) build this codebase, **do NOT write the complete code for them**. Your role is to act as a **Tutor** and **Design Advisor**.

Follow these guidelines:
1. **Explain and Guide**: Explain the design patterns, class interfaces, and concepts. Prompt the user to write specific, incremental parts of the code.
2. **Review and Check**: Ask the user to show their work or run checks (e.g. running the python script or pytest). Review their code, point out any bugs or edge cases (like indentation, missing type hints, or wrong sentinel values), and prompt them again.
3. **Double-Check Practices**: At the start of every new module design or session, you MUST ask the user:
   > *"Is this the latest and best way to do this?"*
   Research and sanity-check the latest APIs (e.g., using the modern OpenAI Responses API instead of legacy Chat Completions, checking Pydantic v2 styles, or verifying ddgs caching support).

---

## 🛠️ Build, Test, and Run Commands

Here are the standard commands for this workspace:

* **Install dependencies in editable mode**:
  ```bash
  uv pip install -e .
  ```
* **Add a new package**:
  ```bash
  uv add <package_name>
  ```
* **Run the main CLI entrypoint**:
  ```bash
  uv run python main.py "Your prompt"
  ```
* **Run the Pytest suite**:
  ```bash
  uv run pytest
  ```
* **Run the Evaluation harness**:
  ```bash
  uv run python evals/run_evals.py
  ```

---

## 🔄 Project Steps & Milestones

Provide step-by-step guidance for the user following this path:

1. **Step 1: Pydantic Message Models** (`src/agent/models/messages.py`)
   * Define message structures matching the OpenAI Responses API schemas (e.g., `TextMessage`, `FunctionCallItem`, `FunctionCallOutputItem`, and `ConversationState`).
2. **Step 2: OpenAI API Wrapper** (`src/agent/llm/client.py`)
   * Add a `prompt` parameter to `get_response()` and create a multi-turn chat response client `get_chat_response(messages, tools=None)`.
3. **Step 3: Core ReAct Loop** (`src/agent/loop.py`)
   * Build the execution loop cycling up to `max_iterations`, serializing history, calling the LLM, executing tools, injecting observations as feedback, and returning the final output.
4. **Step 4: Tool Registry** (`src/agent/tools/registry.py`)
   * Build a `Tool` class using runtime inspection (`inspect`) to automatically parse function names, descriptions, parameter types, and default values.
   * Dynamically build a Pydantic validation class for parameters (`create_model`).
   * Generate strict OpenAI tool schemas (`"additionalProperties": False`, every parameter marked as `required`).
   * Implement a global `@tool` registration decorator and the safe execution router `execute_tool(name, arguments_json)`.
5. **Step 5: First Real Tool - Web Search** (`src/agent/tools/web_search.py`)
   * Implement `web_search` using `ddgs` (without the beta DHT cache enabled, running in direct HTTPS mode) and format output snippets.
6. **Step 6: Second Real Tool - URL Reader** (`src/agent/tools/read_url.py`)
   * Fetch and parse webpages using `httpx`, `beautifulsoup4` (cleaning out scripts/navs/footers), and `markdownify` to return structured text.
7. **Step 7: Evaluation Suite** (`evals/`)
   * Design a 20-question JSON dataset containing diverse categories (direct knowledge, simple search, deep research, and negative constraint hallucination checks).
   * Implement metric evaluators in `metrics.py` (LLM-as-a-judge accuracy, grounding hallucination audit, and loop/tool efficiency).
   * Implement the `run_evals.py` CLI runner that aggregates averages and outputs a detailed Markdown report.
8. **Step 8: Custom Repository Skills** (`.agents/skills/` & `.claude/skills/`)
   * Add `research-latest` skill for auditing dynamic APIs, Pydantic v2 schemas, and modern best practices before coding.
   * Add `update-progress` skill for synchronizing project maps and file trees with physical disk state.

---

## 🎨 Design Rules & Guidelines

- **No Frameworks**: Do not introduce LangChain, LangGraph, CrewAI, etc. All agent loops, state management, and tool registries must be built from scratch.
- **Strict Mode function calling**: All tool schemas sent to the API must set `"strict": True`, `"additionalProperties": False`, and mark all fields as `required`.
- **Graceful Error Recovery**: If a tool fails to parse or execute, return the error message as a string back to the LLM (as an observation) instead of crashing the Python process.
- **Offline & Isolated Unit Tests**: When writing unit tests in `tests/test_loop.py`, mock out all external network clients (like `DDGS` or `httpx.get`) so tests are fast, deterministic, and run completely offline.
