# Mnemosyne Setup Guide

## Prerequisites
- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

## Virtual Environment Setup with Poetry

Poetry does **not** automatically initialize a virtual environment by default when you run `poetry install`. However, it can create one for you under certain conditions:

### How Poetry Handles Virtual Environments:
- **Default behavior**: If no virtual environment is active, Poetry will create a new one in the project's `.venv` directory (or in Poetry's global cache if configured differently).
- **Automatic creation**: Running `poetry install` will automatically create and use a virtual environment if none exists and Poetry is set to manage environments locally.
- **Configuration**: You can control this with `poetry config virtualenvs.in-project true` to ensure it creates `.venv` in your project directory.

### Recommended Steps for Your Project:
1. **Check if Poetry is configured for local virtual environments**:
   ```
   poetry config virtualenvs.in-project
   ```
   If it returns `false`, set it to `true`:
   ```
   poetry config virtualenvs.in-project true
   ```

2. **Install dependencies** (this will create the venv if needed):
   ```
   poetry install
   ```

3. **Activate the virtual environment** (if not already active):
   ```
   poetry shell
   ```
   Or manually: `.\.venv\Scripts\activate` (on Windows)

4. **Verify the environment**:
   ```
   poetry env info
   ```

This way, Poetry handles the virtual environment creation automatically during `poetry install`, keeping your project isolated. If you prefer manual control, you can create the venv yourself with `python -m venv .venv` before running Poetry commands.

## Building and Installing the Package
1. Build the package: `poetry build`
2. Install locally: `pip install dist/mnemosyne-0.1.0-py3-none-any.whl`
3. Test the CLI: `mnemo --help`

## Usage Examples
- `mnemo init` - Initialize data store
- `mnemo agent create "my-agent" --model gpt-4` - Create an agent
- `mnemo workflow run workflow.yaml` - Run a workflow
- `mnemo list --agents` - List agents
- `mnemo dashboard` - Launch TUI dashboard
