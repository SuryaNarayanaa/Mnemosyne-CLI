# Mnemosyne

**Mnemosyne** is a next-generation Python CLI framework for multi-agent orchestration, intelligent workflows, and memory-driven automation, powered by LangChain, LangGraph, Rich, and Textual.

Named after the Greek Titaness of memory and the mother of the Muses, Mnemosyne helps you create, manage, and interact with AI agents and workflows—all in a beautiful and interactive command-line interface.

---

## ✨ Features

- **Multi-Agent Orchestration:** Build and operate teams of AI agents with advanced workflow logic using LangChain + LangGraph.
- **Gorgeous CLI & TUI:** Enjoy visually stunning dashboards, logs, progress bars, and live interfaces with Rich and Textual.
- **Memory & Context:** Agents remember context, past actions, and data—mirroring the power of Mnemosyne herself.
- **Extensible & Modular:** Add your own agents, tools, and workflows with simple Python APIs.
- **Production Ready:** Built-in observability, error handling, checkpointing, and extensible output (JSON/YAML).

---

## 🚀 Quickstart

### Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

### Installation
1. Clone the repository
2. Install dependencies: `poetry install`
3. Build the package: `poetry build`
4. Install the CLI: `pip install dist/mnemosyne-0.1.0-py3-none-any.whl`

### Usage
- `mnemo --help` - Show help
- `mnemo init` - Initialize data store
- `mnemo agent create "my-agent" --model gpt-4` - Create an agent
- `mnemo workflow run workflow.yaml` - Run a workflow
- `mnemo list --agents` - List agents
- `mnemo dashboard` - Launch TUI dashboard
 - `mnemo mcp config view` / `mnemo mcp config set <key> <value>`
 - `mnemo mcp start [cli|fs|git|custom]`

---

## 🔌 MCP Servers

This repo includes multiple MCP servers built with FastMCP 2.0, exposing safe tools to LLM agents over stdio. Each server can be launched as a standalone process and connected from an MCP-compatible client.

### Install deps
Use Poetry to install dependencies, including `fastmcp`:

```
poetry install
```

### CLI Executor Server
Runs allowlisted shell commands and provides system info.

Option A: via env vars (Windows `cmd`):

```
set MNEMO_MCP_CLI_ALLOW=python,git,dir
mnemo-mcp-cli
```

Option B: via Typer subcommands (prompts if missing):

```
mnemo mcp config set cli.allow "python,git,dir"
mnemo mcp start cli
```

Tools:
- `run_command(command, cwd?, timeout_sec?)`
- `system_info()`

### Filesystem Server
Provides safe read/write access rooted at a directory.

Option A: via env vars and run:

```
set MNEMO_MCP_FS_ROOT=%CD%
mnemo-mcp-fs
```

Option B: via Typer subcommands (prompts if missing):

```
mnemo mcp config set fs.root %CD%
mnemo mcp start fs
```

Tools:
- `ls(path=".")`
- `read_file(path, encoding?, max_bytes?)`
- `write_file(path, content, encoding?, overwrite?)`
- `mkdir(path, exist_ok?)`
- `move(src, dest, overwrite?)`
- `delete(path)`

### Git/Version Control Server
Wraps common git commands and optionally GitHub CLI.

Run:

```
mnemo-mcp-git
```

Tools:
- `status(repo_dir=".")`
- `diff(repo_dir=".", path?)`
- `branches(repo_dir=".")`
- `commit(repo_dir=".", message="Update")`
- `create_branch(repo_dir=".", name)`
- `gh_pr_list(repo_dir=".", limit)`

### Custom Tools Server
Sample club tools: event registration, leaderboard, resource sharing.

Run:

```
mnemo-mcp-custom
```

Tools:
- `register_event(user, event)`
- `update_leaderboard(user, delta)`
- `share_resource(title, url, description?)`
- `list_data()`

### Connecting from Clients
These servers speak MCP over stdio; point your MCP client to spawn the respective command, e.g. `mnemo-mcp-fs`. For example, many LLM apps allow configuring an MCP server with a command and args. See FastMCP docs: https://gofastmcp.com/
---

## 🧠 Philosophy

Mnemosyne brings together:

- **Memory:** Agents that learn and adapt contextually.
- **Orchestration:** Multi-step, multi-agent workflows with robust state management.
- **Beauty:** A CLI you’ll love to use every day.

---

## 🏗️ Tech Stack

- **Python 3.9+**
- [LangChain](https://langchain.com/)
- [LangGraph](https://langgraph.com/)
- [Rich](https://github.com/Textualize/rich)
- [Textual](https://github.com/Textualize/textual)
- [Typer](https://github.com/tiangolo/typer)
- Optional: FAISS, Pinecone, Redis for memory/context persistence

---

## 📚 Documentation

- [CLI Reference](https://typer.tiangolo.com/) - Typer documentation
- [LangChain](https://langchain.com/) - For agent definitions
- [LangGraph](https://langgraph.com/) - For workflow orchestration
- [Rich](https://github.com/Textualize/rich) - For CLI output
- [Textual](https://github.com/Textualize/textual) - For TUI dashboard
- [USAGE.md](./USAGE.md) - How to use the included MCP servers

---

## 🙏 Inspiration

> "Mnemosyne is the source of all memory and creativity. Let your agents remember, learn, and create."  

