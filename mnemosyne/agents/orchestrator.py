from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Dict, Optional, TypedDict, List

from langgraph.graph import START, END, StateGraph
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from .github_agent import run_agent as run_github_agent


class OrchestratorState(TypedDict):
    prompt: str
    provider: str
    owner: Optional[str]
    repo: Optional[str]
    route: str
    result: Dict[str, Any]
    trace: List[str]


def _llm(provider: str):
    provider = (provider or "azure").lower()
    if provider == "azure":
        from pydantic import SecretStr
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=SecretStr(os.getenv("AZURE_OPENAI_KEY", "")),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-nano"),
            temperature=0.0,
        )
    else:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.0)


async def classify_node(state: OrchestratorState) -> OrchestratorState:
    # Heuristic first pass to keep routing snappy and obvious
    text = state["prompt"].lower()
    heuristics = ["git ", "github", "commit", "pull request", "pr ", "issue", "workflow", "actions", "repo", "branch", "tag", "release"]
    for h in heuristics:
        if h in text:
            state["route"] = "github"
            state["trace"].append(f"Orchestrator: heuristic match '{h.strip()}' → route=github")
            return state
    llm = _llm(state.get("provider", "azure"))
    system = (
        "You are a router. Respond with a single JSON object {route: 'github'|'default'}. "
        "If the user asks anything about GitHub repos/issues/PRs/actions, pick 'github'."
    )
    state["trace"].append("Orchestrator: analyzing prompt via LLM router")
    msg = await llm.ainvoke([("system", system), ("user", state["prompt"])])
    content = getattr(msg, "content", "{}")
    try:
        data = json.loads(content) if isinstance(content, str) else json.loads(content[0]["text"])  # type: ignore
        route = data.get("route", "default")
    except Exception:
        route = "default"
    state["route"] = route
    state["trace"].append(f"Orchestrator: route={route}")
    return state


async def act_node(state: OrchestratorState) -> OrchestratorState:
    if state.get("route") == "github":
        state["trace"].append("Orchestrator: delegating to GitHub agent")
        # Pass the same trace list into the GitHub agent so it can append its steps
        res = await run_github_agent(
            state["prompt"],
            provider=state.get("provider", "azure"),
            owner=state.get("owner"),
            repo=state.get("repo"),
            trace=state["trace"],
        )
        state["result"] = res
        return state
    state["trace"].append("Orchestrator: no matching agent, default echo")
    state["result"] = {"content": ["No matching agent. Echo:", state["prompt"]], "structured": None}
    return state


def build_graph():
    g = StateGraph(OrchestratorState)

    async def _classify(state: OrchestratorState) -> OrchestratorState:
        return await classify_node(state)

    async def _act(state: OrchestratorState) -> OrchestratorState:
        return await act_node(state)

    g.add_node("classify", _classify)
    g.add_node("act", _act)
    g.add_edge(START, "classify")
    g.add_edge("classify", "act")
    g.add_edge("act", END)
    return g.compile()


async def run_orchestrator(prompt: str, provider: str = "azure", owner: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
    graph = build_graph()
    state: OrchestratorState = {"prompt": prompt, "provider": provider, "owner": owner, "repo": repo, "route": "", "result": {}, "trace": []}
    final = await graph.ainvoke(state)
    return {"trace": final.get("trace", []), "result": final.get("result", {})}
