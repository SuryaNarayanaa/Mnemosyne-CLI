import json
from typing import Any, Dict, List

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


async def connect_with_pat(pat: str):
    headers = {"Authorization": f"Bearer {pat}"}
    return await streamablehttp_client(GITHUB_MCP_URL, headers=headers).__aenter__()


def _flatten_exception_messages(exc: BaseException) -> List[str]:
    if isinstance(exc, BaseExceptionGroup):
        messages: List[str] = []
        for inner in exc.exceptions:
            messages.extend(_flatten_exception_messages(inner))
        return messages
    message = str(exc).strip()
    prefix = exc.__class__.__name__
    return [f"{prefix}: {message}" if message else prefix]


def _parse_text_payload(text: str) -> Any:
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return text


async def list_tools(pat: str) -> list[str]:
    try:
        async with streamablehttp_client(GITHUB_MCP_URL, headers={"Authorization": f"Bearer {pat}"}) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [t.name for t in tools.tools]
    except BaseExceptionGroup as exc:
        messages = _flatten_exception_messages(exc)
        raise RuntimeError("; ".join(messages)) from exc
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc


async def list_tools_full(pat: str) -> dict:
    """Return a mapping of tool name -> {description, inputSchema}"""
    try:
        async with streamablehttp_client(GITHUB_MCP_URL, headers={"Authorization": f"Bearer {pat}"}) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                out = {}
                for t in tools.tools:
                    out[t.name] = {
                        "description": getattr(t, "description", None),
                        "inputSchema": getattr(t, "inputSchema", None),
                        "title": getattr(t, "title", None),
                    }
                return out
    except BaseExceptionGroup as exc:
        messages = _flatten_exception_messages(exc)
        raise RuntimeError("; ".join(messages)) from exc
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc


async def call_tool(pat: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    try:
        async with streamablehttp_client(GITHUB_MCP_URL, headers={"Authorization": f"Bearer {pat}"}) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                data: Dict[str, Any] = {"content": [], "structured": result.structuredContent}
                for c in result.content:
                    try:
                        # Most contents are TextContent with .text
                        text = getattr(c, "text", None)
                        if text:
                            data["content"].append(_parse_text_payload(text))
                    except Exception:
                        pass
                return data
    except BaseExceptionGroup as exc:
        messages = _flatten_exception_messages(exc)
        raise RuntimeError("; ".join(messages)) from exc
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc
