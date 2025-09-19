from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, Optional, TypedDict, cast, List

from langgraph.graph import START, END, StateGraph
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..mcp.github_client import list_tools as gh_list_tools, list_tools_full, call_tool as gh_call_tool
import keyring


GITHUB_PAT_SERVICE = "mnemosyne.github.mcp"


def _get_pat() -> str:
    pat = keyring.get_password(GITHUB_PAT_SERVICE, "pat")
    if not pat:
        raise RuntimeError("GitHub PAT not found. Run 'mnemo github login' first.")
    return pat


def _llm(provider: str):
    provider = provider.lower()
    if provider == "azure":
        from pydantic import SecretStr
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=SecretStr(os.getenv("AZURE_OPENAI_KEY", "")),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano"),
            temperature=0.2,
        )
    elif provider == "gemini":
        # Requires GOOGLE_API_KEY
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
    else:
        raise ValueError("provider must be 'azure' or 'gemini'")


class AgentState(TypedDict):
    prompt: str
    owner: Optional[str]
    repo: Optional[str]
    plan: Dict[str, Any]
    result: Dict[str, Any]
    trace: List[str]


async def plan_node(state: AgentState, provider: str) -> AgentState:
    msg_llm = "GitHub: selecting LLM for planning"
    state["trace"].append(msg_llm)
    print(msg_llm)
    llm = _llm(provider)
    pat = _get_pat()
    msg_tools = "GitHub: fetching tools and schemas from MCP"
    state["trace"].append(msg_tools)
    print(msg_tools)
    tools = await gh_list_tools(pat)
    tool_map = await list_tools_full(pat)
    # Infer owner/repo from git remote if not provided
    if not state.get("owner") or not state.get("repo"):
        own, rep = _infer_owner_repo()
        state["owner"] = state.get("owner") or own
        state["repo"] = state.get("repo") or rep
    system = (
        "You are a planner that maps user requests to GitHub MCP tools. "
        "Select the best tool and produce JSON with 'tool' and 'arguments'. "
        f"Available tools: {tools}. "
        f"If the tool requires owner/repo and user context provides it, include them."
    )
    msg_planning = "GitHub: prompting planner LLM"
    state["trace"].append(msg_planning)
    print(msg_planning)
    msg = await llm.ainvoke([
        ("system", system),
        ("user", state.get("prompt", "")),
    ])
    content = getattr(msg, "content", "{}")
    try:
        plan = json.loads(content) if isinstance(content, str) else json.loads(content[0]["text"])  # type: ignore
    except Exception:
        # Fallback: naive selection
        plan = {"tool": "repos.search_code", "arguments": {"query": state.get("prompt", "")}}
    msg_planned = f"GitHub: planned tool={plan.get('tool')}"
    state["trace"].append(msg_planned)
    print(msg_planned)
    # Autofill owner/repo if required by schema
    input_schema = (tool_map.get(plan.get("tool"), {}) or {}).get("inputSchema") or {}
    required = input_schema.get("required", []) if isinstance(input_schema, dict) else []
    args = plan.get("arguments") or {}
    if "owner" in required and not args.get("owner") and state.get("owner"):
        args["owner"] = cast(Optional[str], state.get("owner"))
    if "repo" in required and not args.get("repo") and state.get("repo"):
        args["repo"] = cast(Optional[str], state.get("repo"))
    if any(k in required for k in ("owner", "repo")):
        msg_autofill = f"GitHub: autofilled owner={args.get('owner')} repo={args.get('repo')}"
        state["trace"].append(msg_autofill)
        print(msg_autofill)
    plan["arguments"] = args
    state["plan"] = plan
    return state


async def act_node(state: AgentState) -> AgentState:
    pat = _get_pat()
    plan = state.get("plan") or {}
    tool = plan.get("tool") or "repos.search_code"
    args = plan.get("arguments", {})
    # Treat placeholders as missing
    for key in ("owner", "repo"):
        if key in args and isinstance(args[key], str) and args[key].strip().lower() in {"owner", "repo", "<owner>", "<repo>"}:
            del args[key]
    # Validate required arguments if schema known
    tool_map = await list_tools_full(pat)
    input_schema = (tool_map.get(tool, {}) or {}).get("inputSchema") or {}
    required = input_schema.get("required", []) if isinstance(input_schema, dict) else []
    missing = [r for r in required if r not in args]
    if missing:
        state["result"] = {
            "content": [
                f"missing required parameter(s): {', '.join(missing)}",
                "Pass --owner and --repo flags, or run from a git repo with a GitHub origin remote, or set defaults.",
            ],
            "structured": None,
        }
        return state
    msg_call = f"GitHub: calling MCP tool {tool}"
    state["trace"].append(msg_call)
    print(msg_call)
    result = await gh_call_tool(pat, tool, args)
    msg_finished = "GitHub: MCP call finished"
    state["trace"].append(msg_finished)
    print(msg_finished)
    state["result"] = result
    return state


async def format_node(state: AgentState) -> AgentState:
    msg_format = "GitHub: formatting result with LLM"
    state["trace"].append(msg_format)
    print(msg_format)
    provider = "azure"  # Use default provider for formatting
    llm = _llm(provider)
    result = state.get("result", {})
    content = result.get("content", [])
    if content:
        # Use LLM to format the content into human-readable text
        system = (
            "You are a formatter that converts raw data into clean, human-readable text. "
            "Format the provided data in a natural, easy-to-read way. "
            "Use bullet points, numbered lists, or paragraphs as appropriate. "
            "Keep it concise but informative."
        )
        data_str = json.dumps(content, indent=2)
        msg = await llm.ainvoke([
            ("system", system),
            ("user", f"Format this data:\n{data_str}"),
        ])
        formatted = getattr(msg, "content", str(content))
        if isinstance(formatted, str):
            state["result"]["content"] = formatted
        else:
            state["result"]["content"] = str(content)
    msg_done = "GitHub: formatting completed"
    state["trace"].append(msg_done)
    print(msg_done)
    return state


def build_graph(provider: str):
    g = StateGraph(AgentState)

    async def _plan(state: AgentState) -> AgentState:
        return await plan_node(state, provider)

    async def _act(state: AgentState) -> AgentState:
        return await act_node(state)

    async def _format(state: AgentState) -> AgentState:
        return await format_node(state)

    g.add_node("plan", _plan)
    g.add_node("act", _act)
    g.add_node("format", _format)
    g.add_edge(START, "plan")
    g.add_edge("plan", "act")
    g.add_edge("act", "format")
    g.add_edge("format", END)
    return g.compile()


async def run_agent(prompt: str, provider: str = "azure", owner: Optional[str] = None, repo: Optional[str] = None, trace: Optional[List[str]] = None) -> Dict[str, Any]:
    graph = build_graph(provider)
    state: AgentState = {"prompt": prompt, "owner": owner, "repo": repo, "plan": {}, "result": {}, "trace": trace or []}
    final = await graph.ainvoke(state)
    return final.get("result", {})


def _infer_owner_repo() -> tuple[Optional[str], Optional[str]]:
    import subprocess, re
    try:
        url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
    except Exception:
        return None, None
    # Match https://github.com/owner/repo(.git)? or git@github.com:owner/repo(.git)?
    m = re.search(r"github\.com[/:]([^/]+)/([^/.]+)", url, re.IGNORECASE)
    if not m:
        return None, None
    return m.group(1), m.group(2)
