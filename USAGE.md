# Mnemosyne MCP Servers — Usage Guide (Windows)

This guide shows how to install, configure, and run the included MCP servers, and how to manage configuration with the `mnemo` CLI.

Servers included:
- CLI Executor: Safely runs allowlisted shell commands
- Filesystem: Read/write files under a confined root
- Git/Version Control: Common git commands, optional GitHub CLI
- Custom Tools: Example tools for events, leaderboard, resources

## Install

Using a virtual environment and pip:

```
python -m venv venv
.\venv\Scripts\activate.bat
pip install -e .
```

Or with Poetry:

```
poetry install
```

## Configuration

The CLI manages config at `%USERPROFILE%\.mnemo\mcp.toml`.

Keys you may set:
- `cli.allow`: comma-separated allowlist for CLI executor (e.g., `python,git,dir`)
- `fs.root`: absolute path for filesystem root confinement

Examples with `mnemo`:

```
mnemo mcp config view
mnemo mcp config set cli.allow "python,git,dir"
mnemo mcp config set fs.root %CD%
```

If a required key is missing when starting a server, the CLI will prompt you and persist the value to the config file automatically.

## Starting Servers

Use Typer subcommands (recommended):

```
mnemo mcp start cli
mnemo mcp start fs
mnemo mcp start git
mnemo mcp start custom
```

These commands read `~/.mnemo/mcp.toml`, set necessary environment variables, and start the respective MCP server via `python -m`.

Start via console scripts (alternative):

```
set MNEMO_MCP_CLI_ALLOW=python,git,dir
mnemo-mcp-cli

set MNEMO_MCP_FS_ROOT=%CD%
mnemo-mcp-fs

mnemo-mcp-git
mnemo-mcp-custom
```

Start directly with Python (alternative):

```
python -m mnemosyne.mcp.cli_executor_server
python -m mnemosyne.mcp.filesystem_server
python -m mnemosyne.mcp.git_server
python -m mnemosyne.mcp.custom_tools_server
```

## What Each Server Exposes

- CLI Executor
  - Tools: `run_command(command, cwd?, timeout_sec?)`, `system_info()`
  - Allowlist env/config: `MNEMO_MCP_CLI_ALLOW` / `cli.allow`
  - The allowlist is matched against the first token of the command (e.g., `python` in `python -m pip --version`). If the first token isn’t in the list, the command won’t run.

- Filesystem
  - Tools: `ls(path=.)`, `read_file(path, ...)`, `write_file(path, ...)`, `mkdir(path, ...)`, `move(src, dest, ...)`, `delete(path)`
  - Root env/config: `MNEMO_MCP_FS_ROOT` / `fs.root`
  - Paths are confined to the root; attempts to escape raise a permission error.

- Git/Version Control
  - Tools: `status(repo_dir=.)`, `diff(...)`, `branches(...)`, `commit(...)`, `create_branch(...)`, `gh_pr_list(...)`
  - `gh_pr_list` requires the GitHub CLI (`gh`) if used

- Custom Tools
  - Tools: `register_event(user, event)`, `update_leaderboard(user, delta)`, `share_resource(title, url, description?)`, `list_data()`

## Using With MCP Clients

These servers speak MCP over stdio. In your MCP-compatible client, configure a server command to spawn, for example:
- Command: `mnemo-mcp-fs` (or `python -m mnemosyne.mcp.filesystem_server`)
- Working directory: your project folder as needed

See the FastMCP docs for client configuration patterns:
https://gofastmcp.com/

## Running Tests

Run tests with `pytest`:

```
.\venv\Scripts\activate.bat
pytest -q
```

Tests include:
- CLI Executor: allowlist permits `python` and blocks others
- Filesystem: root confinement and read/write
- Git: repo status in a temporary repo
- GitHub CLI (optional): PR listing if `gh` is available (skips otherwise)

## Troubleshooting

- If a server refuses to run a command, check `cli.allow` (config) or `MNEMO_MCP_CLI_ALLOW` (env). The executable’s name (first token) must be in the allowlist.
- If file operations fail, ensure `fs.root` points to a valid directory and paths don’t escape the root.
- For GitHub operations, install/auth `gh` if you plan to call `gh_pr_list`.
- You can always bypass console scripts and run `python -m mnemosyne.mcp.<server>` directly to debug.
