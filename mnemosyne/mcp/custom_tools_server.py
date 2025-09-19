import os
from datetime import datetime, timezone
from typing import Dict, List

from fastmcp import FastMCP


_events: List[Dict] = []
_leaderboard: Dict[str, int] = {}
_resources: List[Dict] = []


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


mcp = FastMCP("Mnemo Custom Tools")


@mcp.tool(description="Register a user for an event.")
def register_event(user: str, event: str) -> dict:
    rec = {"user": user, "event": event, "ts": _utcnow()}
    _events.append(rec)
    return {"ok": True, "record": rec}


@mcp.tool(description="Update a user's leaderboard score by delta.")
def update_leaderboard(user: str, delta: int) -> dict:
    _leaderboard[user] = _leaderboard.get(user, 0) + int(delta)
    return {"ok": True, "score": _leaderboard[user]}


@mcp.tool(description="Share a resource with a description and link.")
def share_resource(title: str, url: str, description: str = "") -> dict:
    rec = {"title": title, "url": url, "description": description, "ts": _utcnow()}
    _resources.append(rec)
    return {"ok": True, "resource": rec}


@mcp.tool(description="List current data for events, leaderboard, resources.")
def list_data() -> dict:
    return {
        "events": list(_events),
        "leaderboard": dict(_leaderboard),
        "resources": list(_resources),
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
