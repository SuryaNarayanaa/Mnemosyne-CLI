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

---

## 🙏 Inspiration

> "Mnemosyne is the source of all memory and creativity. Let your agents remember, learn, and create."  

