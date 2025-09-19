import os
import json
import shlex
import subprocess
from typing import List, Optional

from fastmcp import FastMCP


def _get_allowlist() -> List[str]:
    allow = os.getenv("MNEMO_MCP_CLI_ALLOW", "").strip()
    if not allow:
        return []
    return [cmd.strip() for cmd in allow.split(",") if cmd.strip()]


def _within_allowlist(cmd: List[str], allow: List[str]) -> bool:
    if not allow:
        return False
    head = cmd[0].lower()
    return any(head == a.lower() for a in allow)


mcp = FastMCP("Mnemo CLI Executor")


def run_command_impl(command: str, cwd: Optional[str] = None, timeout_sec: int = 120, allowlist: Optional[List[str]] = None) -> dict:
    parts = shlex.split(command, posix=False)
    if allowlist is None:
        allowlist = _get_allowlist()
    if not _within_allowlist(parts, allowlist):
        return {
            "ok": False,
            "error": f"Command '{parts[0] if parts else ''}' not allowed. Allowed: {allowlist}",
        }

    try:
        proc = subprocess.run(
            command,
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            shell=True,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timed out after {timeout_sec}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def system_info_impl() -> dict:
    return {
        "platform": os.name,
        "cwd": os.getcwd(),
        "env_keys": sorted(list(os.environ.keys())),
    }


@mcp.tool(description="Execute a shell command with an allowlist. Returns stdout/stderr.")
def run_command(command: str, cwd: Optional[str] = None, timeout_sec: int = 120) -> dict:
    """
    Execute a shell command if its executable is in the allowlist.

    Args:
        command: Full command line string to execute.
        cwd: Optional working directory.
        timeout_sec: Max seconds to allow the command to run.

    Environment:
        MNEMO_MCP_CLI_ALLOW: comma-separated list of allowed executables (e.g., "python,git,dir").
    """
    return run_command_impl(command, cwd=cwd, timeout_sec=timeout_sec)


@mcp.tool(description="Get basic system information.")
def system_info() -> dict:
    return system_info_impl()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
