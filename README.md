# P01 — ReAct Agent from Scratch

Welcome to **Project 1** of the **Agentic Engineering Bootcamp v2.3**. 

This is a foundational, hands-on learning project designed to build a complete **ReAct (Reasoning + Acting)** research agent from first principles.

---

## 🎯 Project Goal

The primary goal of this project is to build a fully capable, tool-calling research agent using **raw API calls only—without relying on any high-level agent frameworks** (like LangChain, LangGraph, or CrewAI). 

By building the execution flow, state management, and tool integration by hand, we master the underlying mechanics of modern AI agents:
* Managing conversation history as memory.
* Structuring LLM thoughts, actions, and observations.
* Handling tool execution and state synchronization.
* Building evaluation suites to measure accuracy and efficiency.

---

## 🔄 The ReAct Loop Architecture

A ReAct agent combines **Reasoning** (the "Thought") and **Acting** (the "Action"). The agent follows an iterative cycle to solve a user's prompt:

```mermaid
graph TD
    A[Start: User Input] --> B[Initialize Conversation State]
    B --> C[Send conversation history to LLM]
    C --> D[LLM responds with Thought / Action / Final Answer]
    D --> E{Did the LLM call a tool?}
    E -- Yes --> F[Run the tool in Python]
    F --> G[Append Tool Result as Observation]
    G --> C
    E -- No --> H{Did the LLM give a Final Answer?}
    H -- Yes --> I[End: Return Final Answer to User]
    H -- No --> J[Fallback / Stop loop]
```

### The Step-by-Step Cycle:
1. **Thought**: The LLM reasons about the user's request and determines what information it is missing (e.g., *"I need to know the weather in Seattle, so I should call the search tool"*).
2. **Action (Tool Call)**: The LLM chooses a tool and provides the exact parameters to call it.
3. **Observation**: Our code intercepts the tool request, executes the corresponding Python function, and returns the result (the "Observation") to the LLM.
4. **Final Answer**: Once the LLM has gathered enough observations, it synthesizes them and presents the final answer to the user.

---

## 🛠️ Tech Stack & Tooling

* **Python 3.13** — Pinned and managed via `.python-version`.
* **`uv`** — High-performance Rust-based Python package manager and workspace tool.
* **OpenAI Responses API** — Utilizing `client.responses.create()`, the modern standard for interacting with frontier models (like `gpt-5.4-mini`).
* **Pydantic v2** — Used for robust runtime data validation and state modeling.

---

## 📁 Codebase Structure

```
p01-react-agent/
├── main.py                        # Thin CLI entry point
├── pyproject.toml                 # Project metadata and dependencies
├── .vscode/
│   └── settings.json              # VS Code path resolutions for Pylance
├── src/
│   └── agent/
│       ├── __init__.py
│       ├── config.py              # Loads settings from .env using Pydantic Settings
│       ├── loop.py                # Core ReAct loop implementation (In Progress)
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py          # OpenAI Responses API wrapper
│       └── models/
│           ├── __init__.py
│           └── messages.py        # Pydantic models for Message and ConversationState
```

---

## 🚀 How to Run the Project

1. **Environment Setup**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY="your-api-key"
   MODEL="gpt-5.4-mini"
   ```

2. **Install Dependencies**:
   Install the project and its dependencies in editable mode:
   ```bash
   uv pip install -e .
   ```

3. **Run the Entrypoint**:
   ```bash
   uv run main.py "Your prompt here"
   ```
