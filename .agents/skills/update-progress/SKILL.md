---
name: update-progress
description: Keep CLAUDE.md and AGENTS.md project roadmap trees synchronized with files completed on disk.
---

# Update Progress Skill

Use this skill whenever you complete a project milestone, create a file, or verify a step (like loop.py, registry.py, tools, or metrics).

## Guidelines

1. **Documentation Synchronization**:
   Whenever a file is successfully created and verified, you MUST update its status in the codebase structure lists in:
   - `CLAUDE.md` (under "Planned file structure" or "Completed file structure" and "Immediate next steps")
   - `AGENTS.md` (under "Project Steps & Milestones")

2. **File Tree Status Flags**:
   - `(completed)`: Files that exist on disk, are fully written, and have passed tests.
   - `(not yet created)`: Files that do not yet exist on disk.

3. **Roadmap Integrity**:
   - Remove completed items from the "Immediate next steps" list.
   - Push the next uncreated file/milestone to the top of the "Immediate next steps" list.
   - Always ensure that `CLAUDE.md` and `AGENTS.md` match the real, physical state of the directory on disk.
