import asyncio
import os
from typing import Any, Dict, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


async def connect_with_pat(pat: str):
    headers = {"Authorization": f"Bearer {pat}"}
    return await streamablehttp_client(GITHUB_MCP_URL, headers=headers).__aenter__()


async def list_tools(pat: str) -> list[str]:
    async with streamablehttp_client(GITHUB_MCP_URL, headers={"Authorization": f"Bearer {pat}"}) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [t.name for t in tools.tools]


async def list_tools_full(pat: str) -> dict:
    """Return a mapping of tool name -> {description, inputSchema}"""
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


async def call_tool(pat: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
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
                        data["content"].append(text)
                except Exception:
                    pass
            return data
