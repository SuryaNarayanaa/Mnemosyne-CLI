import json
import os
import shlex
import subprocess
from typing import List, Optional

from fastmcp import FastMCP


def _run(cmd: List[str], cwd: Optional[str] = None, timeout: int = 60) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


mcp = FastMCP("Mnemo Git")


def status_impl(repo_dir: str = ".") -> dict:
    return _run(["git", "status", "--porcelain=v2"], cwd=repo_dir)


@mcp.tool(description="Get git status in the given repo directory")
def status(repo_dir: str = ".") -> dict:
    return status_impl(repo_dir)


def diff_impl(repo_dir: str = ".", path: Optional[str] = None) -> dict:
    cmd = ["git", "diff"]
    if path:
        cmd.append(path)
    return _run(cmd, cwd=repo_dir)


@mcp.tool(description="Show diff for the repo (optionally a path).")
def diff(repo_dir: str = ".", path: Optional[str] = None) -> dict:
    return diff_impl(repo_dir, path)


def branches_impl(repo_dir: str = ".") -> dict:
    return _run(["git", "branch", "--all", "--verbose"], cwd=repo_dir)


@mcp.tool(description="List branches in the repo.")
def branches(repo_dir: str = ".") -> dict:
    return branches_impl(repo_dir)


def commit_impl(repo_dir: str = ".", message: str = "Update") -> dict:
    return _run(["git", "commit", "-m", message], cwd=repo_dir)


@mcp.tool(description="Commit staged changes with a message.")
def commit(repo_dir: str = ".", message: str = "Update") -> dict:
    return commit_impl(repo_dir, message)


def create_branch_impl(repo_dir: str = ".", name: str = "feature/temp") -> dict:
    return _run(["git", "checkout", "-b", name], cwd=repo_dir)


@mcp.tool(description="Create a new branch.")
def create_branch(repo_dir: str = ".", name: str = "feature/temp") -> dict:
    return create_branch_impl(repo_dir, name)


def gh_pr_list_impl(repo_dir: str = ".", limit: int = 10) -> dict:
    gh_cmd = ["gh", "pr", "list", "--limit", str(limit)]
    return _run(gh_cmd, cwd=repo_dir)


@mcp.tool(description="List PRs via GitHub CLI if available.")
def gh_pr_list(repo_dir: str = ".", limit: int = 10) -> dict:
    return gh_pr_list_impl(repo_dir, limit)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
