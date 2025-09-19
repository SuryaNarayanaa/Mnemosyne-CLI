from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict


def config_dir() -> Path:
    base = Path.home() / ".mnemo"
    base.mkdir(parents=True, exist_ok=True)
    return base


def config_path() -> Path:
    return config_dir() / "mcp.toml"


def load_config() -> Dict[str, Any]:
    p = config_path()
    if not p.exists():
        return {}
    try:
        import tomllib  # py>=3.11
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def _to_toml(data: Dict[str, Any]) -> str:
    # Minimal TOML writer for flat section->key->value (str only)
    lines: list[str] = []
    for section, values in data.items():
        if not isinstance(values, dict):
            continue
        lines.append(f"[{section}]")
        for k, v in values.items():
            vs = str(v).replace("\n", " ")
            lines.append(f"{k} = \"{vs}\"")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def save_config(data: Dict[str, Any]) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_to_toml(data), encoding="utf-8")


def get_cli_allow(cfg: Dict[str, Any]) -> str | None:
    return (cfg.get("cli") or {}).get("allow")


def set_cli_allow(cfg: Dict[str, Any], value: str) -> Dict[str, Any]:
    d = dict(cfg)
    d.setdefault("cli", {})
    d["cli"]["allow"] = value
    return d


def get_fs_root(cfg: Dict[str, Any]) -> str | None:
    return (cfg.get("fs") or {}).get("root")


def set_fs_root(cfg: Dict[str, Any], value: str) -> Dict[str, Any]:
    d = dict(cfg)
    d.setdefault("fs", {})
    d["fs"]["root"] = value
    return d
