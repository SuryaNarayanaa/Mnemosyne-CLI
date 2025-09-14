# Mnemosyne – AI Assistant Working Agreement

Status: Scaffold created before code exists. Revise aggressively as code is added.

## Purpose
Provide immediately actionable constraints so AI agents can help bootstrap a reliable cross-platform multi-agent orchestration CLI tool ("Mnemosyne") from an empty repository. Update this file as architecture, commands, and modules emerge.

## Core Objectives (Initial Phase)
1. Stand up minimal runnable CLI skeleton (argument parsing, version flag, help text) using Typer.
2. Define data models for agents, workflows, and memory persistence (e.g., JSON, SQLite, or vector DB like FAISS/Pinecone).
3. Implement multi-agent orchestration core using LangChain + LangGraph for workflow logic and state management.
4. Provide import/export (initially JSON) for agent configurations and workflow backups.
5. Ensure Windows-first usability while remaining portable (no POSIX-only assumptions).

## Early Architectural Guidance
- Language: Python 3.9+ with Typer for CLI, Rich for output, Textual for TUI.
- Modular boundaries to plan for:
  - `agents` layer (define and manage AI agents).
  - `workflows` (orchestrate multi-step processes with LangGraph).
  - `memory` (handle context persistence; swappable backend like Redis or local files).
  - `cli` (parsing + subcommand handlers only; no business logic inline).
  - `core` orchestrating agents + workflows + memory.
- Keep pure logic (orchestration rules) free of I/O for easy unit testing.

## Conventions To Establish Early
- Use UTC timestamps for memory and logs; format for display at edge.
- Separate domain errors (e.g., AgentNotFound) vs generic exceptions.
- Prefer dependency injection via simple factory functions over globals/singletons.
- Keep command functions small: parse → call core service → render output with Rich.
- Add docstring on public functions specifying side effects + return types (concise).

## Suggested Initial Command Set
- `mnemo init` – create data store structure for agents/workflows.
- `mnemo agent create "name" --model gpt-4` – add new agent.
- `mnemo workflow run "workflow.yaml"` – execute a workflow.
- `mnemo list [--agents|--workflows]` – list agents or workflows.
- `mnemo export FILE` / `mnemo import FILE` – backup/restore configurations.
- `mnemo dashboard` – launch Textual TUI for monitoring.

## Tech Stack Integration
- LangChain for agent definitions and tool integrations.
- LangGraph for workflow graphs and state transitions.
- Rich for CLI output formatting (tables, progress bars).
- Textual for interactive dashboards.
- Optional: FAISS/Pinecone for vector memory, Redis for session persistence.

## Testing Strategy (Foundational)
- Unit test orchestration logic first (edge cases: agent failures, workflow loops).
- Test CLI commands with snapshot outputs.
- For TUI, test key interactions programmatically.

## Cross-Platform Notes (Windows Emphasis)
- Avoid hardcoded `~`; use `pathlib.Path.home()`.
- Use Rich's auto-detection for colored output.
- File locks: rely on SQLite or Redis rather than custom locks.

## Performance / Scale Assumptions (Initial)
- Target <= 100 agents/workflows; optimize for memory usage.
- Profile LangChain calls; avoid premature micro-opts.

## Documentation & Evolution
- Keep this file updated at each architectural milestone (e.g., first agent created, workflow executed).
- Add a high-level README once first runnable CLI exists (install, usage examples).

## AI Assistant Directives
- Before adding code, confirm tech stack if still undecided.
- Propose minimal incremental changes; do not dump monolith.
- Generate commands with idempotent behavior (running `init` twice is safe).
- Surface tradeoffs (e.g., FAISS vs Pinecone) succinctly when implementing.
- Ask for clarification if a decision remains ambiguous after one reasonable assumption.

## Out of Scope (For Now)
- Cloud deployment / multi-device sync.
- Advanced GUI beyond Textual TUI.
- Encryption for memory data (flag later if needed).

---
Revise this file once real code lands: add concrete filenames, module examples, and workflow commands.