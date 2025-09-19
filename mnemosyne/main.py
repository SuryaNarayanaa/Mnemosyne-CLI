import os
import subprocess
import sys
from typing import Optional
import typer
from .display import print_banner, print_success_message
from .config import (
    load_config,
    save_config,
    get_cli_allow,
    set_cli_allow,
    get_fs_root,
    set_fs_root,
)
import keyring
import asyncio
from .mcp.github_client import list_tools as gh_list_tools, call_tool as gh_call_tool
from .agents.github_agent import run_agent as run_github_agent


app = typer.Typer()

mcp_app = typer.Typer(help="Manage and run MCP servers")
app.add_typer(mcp_app, name="mcp")

gh_app = typer.Typer(help="Use GitHub hosted MCP from CLI")
app.add_typer(gh_app, name="github")


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    provider: str = typer.Option("azure", help="Default provider for interactive mode"),
    owner: Optional[str] = typer.Option(None, help="Default GitHub owner/org"),
    repo: Optional[str] = typer.Option(None, help="Default GitHub repo name"),
):
    """
    Mnemosyne: AI Assistant CLI for multi-agent orchestration
    """
    print_banner()
    print_success_message("Data store initialized.")
    # Enter REPL automatically when no subcommand is provided
    if ctx.invoked_subcommand is None:
        repl(provider=provider, owner=owner, repo=repo)


@app.command("repl")
def repl(provider: str = typer.Option("azure", help="Default model provider"), owner: Optional[str] = typer.Option(None), repo: Optional[str] = typer.Option(None)):
    """Interactive Mnemosyne mode. Type 'exit' to quit."""
    from .agents.orchestrator import run_orchestrator
    while True:
        try:
            prompt = input("mnemo> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit"}:
            break
        import json as _json
        res = asyncio.run(run_orchestrator(prompt, provider=provider, owner=owner, repo=repo))
        result = res.get("result", {})
        # Format result human-readably
        if "content" in result:
            content = result["content"]
            if isinstance(content, str):
                print("\n--- Result ---")
                print(content)
            elif isinstance(content, list) and content and isinstance(content[0], dict):
                # Fallback formatting
                print("\n--- Result ---")
                for i, item in enumerate(content, 1):
                    name = item.get("name", "Unknown")
                    full_name = item.get("full_name", name)
                    desc = item.get("description", "No description")
                    stars = item.get("stargazers_count", 0)
                    language = item.get("language", "")
                    print(f"{i}. {name} ({full_name})")
                    if desc:
                        print(f"   Description: {desc}")
                    if stars:
                        print(f"   Stars: {stars}")
                    if language:
                        print(f"   Language: {language}")
                    print()
            elif isinstance(content, list):
                print("\n--- Result ---")
                for item in content:
                    print(item)
            else:
                print(f"\nResult: {content}")
        if result.get("structured"):
            print(f"Structured: {result['structured']}")
        print("-------------")


@app.command("start")
def start(provider: str = typer.Option("azure", help="Default provider")):
    """Start Mnemosyne in interactive mode (alias for repl)."""
    repl(provider=provider)


@app.command()
def help():
    """
    List available features and commands
    """
    print_banner()
    typer.echo("• init - Initialize data store structure for agents and workflows")
    typer.echo("• agent-create - Create a new AI agent")
    typer.echo("• workflow-run - Execute a workflow from YAML file")
    typer.echo("• list - List agents or workflows")
    typer.echo("• export - Export configurations to file")
    typer.echo("• import-config - Import configurations from file")
    typer.echo("• dashboard - Launch Textual TUI dashboard")
    typer.echo("• mcp start [cli|fs|git|custom] - Run MCP servers")
    typer.echo("• mcp config [view|set] - Manage MCP config")
    typer.echo("• github login|tools|call - Use GitHub hosted MCP")
    typer.echo("• agent-github - Run GitHub agent (LangGraph)")
    typer.echo("• help - Show this list of features")
    typer.echo("\nUse 'python -m mnemosyne <command> --help' for more details on each command.")


def _spawn(cmd: list[str]):
    # Spawn a subprocess that runs until user cancels
    return subprocess.call(cmd)


GITHUB_PAT_SERVICE = "mnemosyne.github.mcp"


def _store_pat(pat: str):
    keyring.set_password(GITHUB_PAT_SERVICE, "pat", pat)


def _load_pat() -> str | None:
    return keyring.get_password(GITHUB_PAT_SERVICE, "pat")


@gh_app.command("login")
def github_login(pat: Optional[str] = typer.Option(None, help="GitHub Personal Access Token (or set GITHUB_TOKEN/GITHUB_PERSONAL_ACCESS_TOKEN)")):
    if not pat:
        # Try common env var names first for non-interactive usage
        pat = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not pat:
        pat = typer.prompt("Enter GitHub Personal Access Token", hide_input=True)
    assert pat is not None
    _store_pat(pat)
    typer.echo("PAT stored securely.")


@gh_app.command("tools")
def github_tools():
    pat = _load_pat()
    if not pat:
        raise typer.Exit(code=1)
    names = asyncio.run(gh_list_tools(pat))
    for n in names:
        typer.echo(n)


@gh_app.command("call")
def github_call(tool: str, args: str = typer.Option("{}", help="JSON dict of arguments")):
    import json as _json
    pat = _load_pat()
    if not pat:
        raise typer.Exit(code=1)
    try:
        arguments = _json.loads(args)
    except Exception:
        typer.echo("Invalid JSON for --args")
        raise typer.Exit(code=2)
    result = asyncio.run(gh_call_tool(pat, tool, arguments))
    typer.echo(_json.dumps(result, indent=2))


@app.command("agent-github")
def agent_github(
    prompt: str = typer.Argument(..., help="What should GitHub do?"),
    provider: str = typer.Option("azure", help="azure|gemini"),
    owner: Optional[str] = typer.Option(None, help="GitHub owner/org"),
    repo: Optional[str] = typer.Option(None, help="GitHub repo name"),
):
    result = asyncio.run(run_github_agent(prompt, provider=provider, owner=owner, repo=repo))
    # Format result human-readably
    if "content" in result:
        content = result["content"]
        if isinstance(content, str):
            typer.echo("--- Result ---")
            typer.echo(content)
        elif isinstance(content, list) and content and isinstance(content[0], dict):
            # Fallback formatting
            typer.echo("--- Result ---")
            for i, item in enumerate(content, 1):
                name = item.get("name", "Unknown")
                full_name = item.get("full_name", name)
                desc = item.get("description", "No description")
                stars = item.get("stargazers_count", 0)
                language = item.get("language", "")
                typer.echo(f"{i}. {name} ({full_name})")
                if desc:
                    typer.echo(f"   Description: {desc}")
                if stars:
                    typer.echo(f"   Stars: {stars}")
                if language:
                    typer.echo(f"   Language: {language}")
                typer.echo()
        elif isinstance(content, list):
            typer.echo("--- Result ---")
            for item in content:
                typer.echo(item)
        else:
            typer.echo(f"Result: {content}")
    if result.get("structured"):
        typer.echo(f"Structured: {result['structured']}")
    typer.echo("-------------")


@mcp_app.command("start")
def mcp_start(kind: str = typer.Argument(..., help="cli|fs|git|custom")):
    """Start one of the MCP servers."""
    cfg = load_config()

    if kind == "cli":
        allow = get_cli_allow(cfg)
        if not allow:
            allow = typer.prompt("Enter allowlist for CLI executor (comma-separated)", default="python,git,dir")
            cfg = set_cli_allow(cfg, allow)
            save_config(cfg)
        env = dict(os.environ)
        env["MNEMO_MCP_CLI_ALLOW"] = allow
        rc = subprocess.call([sys.executable, "-m", "mnemosyne.mcp.cli_executor_server"], env=env)
        raise typer.Exit(code=rc)

    if kind == "fs":
        root = get_fs_root(cfg)
        if not root:
            root = typer.prompt("Enter filesystem root (absolute path)", default=os.getcwd())
            cfg = set_fs_root(cfg, root)
            save_config(cfg)
        env = dict(os.environ)
        env["MNEMO_MCP_FS_ROOT"] = root
        rc = subprocess.call([sys.executable, "-m", "mnemosyne.mcp.filesystem_server"], env=env)
        raise typer.Exit(code=rc)

    if kind == "git":
        rc = subprocess.call([sys.executable, "-m", "mnemosyne.mcp.git_server"]) 
        raise typer.Exit(code=rc)

    if kind == "custom":
        rc = subprocess.call([sys.executable, "-m", "mnemosyne.mcp.custom_tools_server"]) 
        raise typer.Exit(code=rc)

    typer.echo("Unknown kind. Use one of: cli, fs, git, custom")
    raise typer.Exit(code=2)


@mcp_app.command("config")
def mcp_config(
    action: str = typer.Argument(..., help="view or set"),
    key: str = typer.Argument(None, help="Key to set: cli.allow or fs.root", show_default=False),
    value: str = typer.Argument(None, help="Value to set", show_default=False),
):
    """View or set MCP config in ~/.mnemo/mcp.toml"""
    cfg = load_config()
    if action == "view":
        typer.echo(cfg)
        return
    if action == "set":
        if not key or value is None:
            typer.echo("Usage: mnemo mcp config set <cli.allow|fs.root> <value>")
            raise typer.Exit(code=2)
        if key == "cli.allow":
            cfg = set_cli_allow(cfg, value)
        elif key == "fs.root":
            cfg = set_fs_root(cfg, value)
        else:
            typer.echo("Unknown key; use cli.allow or fs.root")
            raise typer.Exit(code=2)
        save_config(cfg)
        typer.echo("Saved.")
        return
    typer.echo("Unknown action. Use: view | set")
    raise typer.Exit(code=2)


    
    