from __future__ import annotations

import asyncio
import json
import os
import difflib
from typing import Any, Dict, Optional, TypedDict, cast, List, Tuple

from langgraph.graph import START, END, StateGraph
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from ..mcp.github_client import list_tools as gh_list_tools, list_tools_full, call_tool as gh_call_tool
import keyring


GITHUB_PAT_SERVICE = "mnemosyne.github.mcp"


def _get_pat() -> str:
    pat = keyring.get_password(GITHUB_PAT_SERVICE, "pat")
    if not pat:
        raise RuntimeError("GitHub PAT not found. Run 'mnemo github login' first.")
    return pat


def _llm(provider: str) -> Tuple[Any, str]:
    desired = (provider or "azure").lower()
    if desired == "azure":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        key = os.getenv("AZURE_OPENAI_KEY")
        if endpoint and key:
            return (
                AzureChatOpenAI(
                    azure_endpoint=endpoint,
                    api_key=SecretStr(key),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano"),
                ),
                "azure",
            )
        # Fall back to Gemini if Azure creds missing
        desired = "gemini"
    if desired == "gemini":
        if os.getenv("GOOGLE_API_KEY"):
            return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2), "gemini"
        raise RuntimeError(
            "No LLM provider configured. Set Azure OpenAI environment variables or GOOGLE_API_KEY, "
            "or pass --provider gemini after configuring Google Generative AI."
        )
    raise ValueError("provider must be 'azure' or 'gemini'")


class AgentState(TypedDict):
    prompt: str
    owner: Optional[str]
    repo: Optional[str]
    plan: Dict[str, Any]
    result: Dict[str, Any]
    trace: List[str]
    llm_provider: str


async def plan_node(state: AgentState, provider: str) -> AgentState:
    msg_llm = "GitHub: selecting LLM for planning"
    state["trace"].append(msg_llm)
    print(msg_llm)
    try:
        llm, resolved_provider = _llm(state.get("llm_provider") or provider)
        state["llm_provider"] = resolved_provider
        if resolved_provider != (provider or "azure").lower():
            msg_fallback = f"GitHub: falling back to {resolved_provider} provider"
            state["trace"].append(msg_fallback)
            print(msg_fallback)
    except RuntimeError as exc:
        error_msg = f"GitHub: LLM unavailable - {exc}"
        state["trace"].append(error_msg)
        print(error_msg)
        state["result"] = {"content": [str(exc)], "structured": None}
        state["plan"] = {}
        return state

    try:
        pat = _get_pat()
    except RuntimeError as exc:
        error_msg = f"GitHub: {exc}"
        state["trace"].append(error_msg)
        print(error_msg)
        state["result"] = {"content": [str(exc)], "structured": None}
        state["plan"] = {}
        return state

    msg_tools = "GitHub: fetching tools and schemas from MCP"
    state["trace"].append(msg_tools)
    print(msg_tools)
    try:
        tools = await gh_list_tools(pat)
        tool_map = await list_tools_full(pat)
    except Exception as exc:
        error_msg = f"GitHub: failed to list tools - {exc}"
        state["trace"].append(error_msg)
        print(error_msg)
        state["result"] = {"content": ["Unable to retrieve GitHub tools.", str(exc)], "structured": None}
        state["plan"] = {}
        return state
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
    if plan.get("tool") not in tool_map:
        msg_missing = f"GitHub: tool '{plan.get('tool')}' not available in GitHub MCP"
        state["trace"].append(msg_missing)
        print(msg_missing)
        suggestions = difflib.get_close_matches(plan.get("tool"), list(tool_map.keys()), n=3)
        hint = (
            f"Tool '{plan.get('tool')}' is not available."
            + (f" Did you mean: {', '.join(suggestions)}?" if suggestions else " Use 'mnemo github tools' to list supported tools.")
        )
        state["result"] = {"content": hint, "structured": None}
        state["plan"] = {}
        return state
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


def _fallback_format(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        try:
            return json.dumps(content, indent=2, ensure_ascii=False)
        except TypeError:
            return "\n".join(str(item) for item in content)
    if isinstance(content, dict):
        return json.dumps(content, indent=2, ensure_ascii=False)
    return str(content)


async def act_node(state: AgentState) -> AgentState:
    plan = state.get("plan") or {}
    if not plan.get("tool"):
        return state
    pat = _get_pat()
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
    try:
        result = await gh_call_tool(pat, tool, args)
    except Exception as exc:
        error_msg = f"GitHub: MCP call failed - {exc}"
        state["trace"].append(error_msg)
        print(error_msg)
        state["result"] = {"content": f"GitHub MCP call failed: {exc}", "structured": None}
        return state
    msg_finished = "GitHub: MCP call finished"
    state["trace"].append(msg_finished)
    print(msg_finished)
    state["result"] = result
    return state


async def format_node(state: AgentState, provider: str) -> AgentState:
    result = state.get("result", {})
    content = result.get("content")
    if not content:
        return state
    if isinstance(content, str):
        return state

    msg_format = "GitHub: formatting result with LLM"
    state["trace"].append(msg_format)
    print(msg_format)

    effective_provider = state.get("llm_provider") or provider
    try:
        llm, resolved_provider = _llm(effective_provider)
        state["llm_provider"] = resolved_provider
    except RuntimeError as exc:
        fallback_msg = f"GitHub: formatting fallback - {exc}"
        state["trace"].append(fallback_msg)
        print(fallback_msg)
        state["result"]["content"] = _fallback_format(content)
        return state

    system = (
        "You are a formatter that converts raw data into clean, human-readable text. "
        "Format the provided data in a natural, easy-to-read way. "
        "Use bullet points, numbered lists, or short paragraphs as appropriate. "
        "Keep it concise but informative."
    )
    data_str = json.dumps(content, indent=2, ensure_ascii=False)
    msg = await llm.ainvoke([
        ("system", system),
        ("user", f"Format this data in a human-friendly way:\n{data_str}"),
    ])
    formatted = getattr(msg, "content", None)
    if isinstance(formatted, str):
        state["result"]["content"] = formatted
    elif isinstance(formatted, list):
        state["result"]["content"] = "\n".join(str(part) for part in formatted)
    else:
        state["result"]["content"] = _fallback_format(content)

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
        return await format_node(state, provider)

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
    state: AgentState = {
        "prompt": prompt,
        "owner": owner,
        "repo": repo,
        "plan": {},
        "result": {},
        "trace": trace or [],
        "llm_provider": (provider or "azure").lower(),
    }
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
