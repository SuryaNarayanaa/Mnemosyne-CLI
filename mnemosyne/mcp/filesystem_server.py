import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP


def _root() -> Path:
    val = os.getenv("MNEMO_MCP_FS_ROOT", os.getcwd())
    p = Path(val).resolve()
    return p


def _resolve(path: str) -> Path:
    base = _root()
    target = (base / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not str(target).startswith(str(base)):
        raise PermissionError("Path escapes the FS root")
    return target


mcp = FastMCP("Mnemo Filesystem")


def ls_impl(path: str = "."):
    root = _resolve(path)
    if not root.exists():
        return []
    items = []
    for child in sorted(root.iterdir()):
        items.append({
            "name": child.name,
            "is_dir": child.is_dir(),
            "size": child.stat().st_size if child.is_file() else None,
        })
    return items


@mcp.tool(description="List directory entries relative to FS root.")
def ls(path: str = ".") -> List[dict]:
    return ls_impl(path)


def read_file_impl(path: str, encoding: str = "utf-8", max_bytes: int = 1024 * 1024) -> dict:
    p = _resolve(path)
    if not p.exists() or not p.is_file():
        return {"ok": False, "error": "File not found"}
    if p.stat().st_size > max_bytes:
        return {"ok": False, "error": "File too large"}
    content = p.read_text(encoding=encoding)
    return {"ok": True, "content": content}


@mcp.tool(description="Read a text file under FS root.")
def read_file(path: str, encoding: str = "utf-8", max_bytes: int = 1024 * 1024) -> dict:
    return read_file_impl(path, encoding=encoding, max_bytes=max_bytes)


def write_file_impl(path: str, content: str, encoding: str = "utf-8", overwrite: bool = True) -> dict:
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and not overwrite:
        return {"ok": False, "error": "File exists and overwrite=False"}
    p.write_text(content, encoding=encoding)
    return {"ok": True}


@mcp.tool(description="Write text to a file under FS root. Creates parents if needed.")
def write_file(path: str, content: str, encoding: str = "utf-8", overwrite: bool = True) -> dict:
    return write_file_impl(path, content, encoding=encoding, overwrite=overwrite)


def mkdir_impl(path: str, exist_ok: bool = True) -> dict:
    p = _resolve(path)
    p.mkdir(parents=True, exist_ok=exist_ok)
    return {"ok": True}


@mcp.tool(description="Create a directory under FS root.")
def mkdir(path: str, exist_ok: bool = True) -> dict:
    return mkdir_impl(path, exist_ok=exist_ok)


def move_impl(src: str, dest: str, overwrite: bool = False) -> dict:
    sp = _resolve(src)
    dp = _resolve(dest)
    if dp.exists() and not overwrite:
        return {"ok": False, "error": "Destination exists and overwrite=False"}
    dp.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(sp), str(dp))
    return {"ok": True}


@mcp.tool(description="Move or rename a file/directory under FS root.")
def move(src: str, dest: str, overwrite: bool = False) -> dict:
    return move_impl(src, dest, overwrite=overwrite)


def delete_impl(path: str) -> dict:
    p = _resolve(path)
    if p.is_dir():
        shutil.rmtree(p)
    elif p.exists():
        p.unlink()
    return {"ok": True}


@mcp.tool(description="Delete a file or directory under FS root.")
def delete(path: str) -> dict:
    return delete_impl(path)

def main():
    mcp.run()


if __name__ == "__main__":
    main()
