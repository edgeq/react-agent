---
name: research-latest
description: Research the latest and best approaches for libraries, API schemas, and tools before suggesting code updates.
---

# Research Latest Approach Skill

Use this skill when you are starting a new session, refactoring code, or introducing new features (like Pydantic models, API client requests, or library integrations).

## Guidelines

1. **Verify Before Coding**:
   Do not assume your pre-trained parametric memory is up-to-date for dynamic libraries or third-party APIs. Always research and double-check:
   - Modern API structures (e.g., OpenAI Responses API vs. legacy Chat Completions).
   - Python library version features (e.g., Pydantic v2 vs. v1 models, or Pydantic Settings env loading).
   - Web search scraping library API changes (e.g., `duckduckgo-search` / `ddgs` class names).

2. **Sanity Check**:
   Before proposing any design or code changes, you MUST explicitly ask the user:
   > *"Is this the latest and best way to do this?"*
   Present any modern improvements or alternatives discovered during your research.

3. **Required Actions**:
   - Run a web search or view documentation URLs for the library/API in question to see if there are newer versions or deprecation warnings.
   - Look for security compliance requirements and performance optimizations.
