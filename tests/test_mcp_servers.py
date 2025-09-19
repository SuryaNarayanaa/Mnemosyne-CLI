import os
import sys
import subprocess
from pathlib import Path

import pytest


def run_module(mod: str, env: dict | None = None, timeout: int = 5):
    return subprocess.Popen([sys.executable, "-m", mod], env=env or os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_cli_executor_allowlist(tmp_path: Path):
    env = os.environ.copy()
    env["MNEMO_MCP_CLI_ALLOW"] = "python"
    # quick import check
    __import__("mnemosyne.mcp.cli_executor_server")
    # Directly invoke function for speed rather than full MCP session
    from mnemosyne.mcp.cli_executor_server import run_command_impl

    ok = run_command_impl(f"{sys.executable} -c \"print('hi')\"", allowlist=["python"])
    assert ok["ok"]
    assert "hi" in ok["stdout"]

    blocked = run_command_impl("git status", allowlist=["python"])
    assert not blocked["ok"]


def test_filesystem_root_confined(tmp_path: Path, monkeypatch):
    from mnemosyne.mcp.filesystem_server import write_file_impl, read_file_impl, _resolve
    monkeypatch.setenv("MNEMO_MCP_FS_ROOT", str(tmp_path))
    # write and read within root
    res = write_file_impl("a/b.txt", "hello")
    assert res["ok"]
    rd = read_file_impl("a/b.txt")
    assert rd["ok"] and rd["content"] == "hello"
    # attempt escape
    with pytest.raises(PermissionError):
        _resolve("..\\..\\secret.txt")


def test_git_server_status(tmp_path: Path):
    # init a new repo
    subprocess.check_call(["git", "init"], cwd=tmp_path)
    p = tmp_path / "x.txt"
    p.write_text("x")
    subprocess.check_call(["git", "add", "x.txt"], cwd=tmp_path)
    from mnemosyne.mcp.git_server import status_impl
    out = status_impl(str(tmp_path))
    assert out["ok"]


def test_gh_cli_optional(tmp_path: Path):
    from shutil import which
    from mnemosyne.mcp.git_server import gh_pr_list_impl
    if which("gh") is None:
        pytest.skip("gh not installed")
    out = gh_pr_list_impl(str(tmp_path), limit=1)
    # Should run; ok may be False if not authenticated, but command executes
    assert "returncode" in out or "error" in out
