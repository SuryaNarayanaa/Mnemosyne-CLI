import os
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Define state
class State(TypedDict):
    question: str
    llm: object
    researcher_output: str
    summarizer_output: str
    critic_output: str
    consensus_output: str

load_dotenv()

# --- Debate Agent Roles ---
def researcher(state: State):
    q = state["question"]
    response = state["llm"].invoke(
        f"As researcher, give evidence in <=300 characters:\n{q}",
        generation_config={"max_output_tokens": 80}
    )
    state["researcher_output"] = response.content.strip()
    return state

def summarizer(state: State):
    response = state["llm"].invoke(
        f"As summarizer, condense in <=300 characters:\n{state['researcher_output']}",
        generation_config={"max_output_tokens": 80}
    )
    state["summarizer_output"] = response.content.strip()
    return state

def critic(state: State):
    response = state["llm"].invoke(
        f"As critic, refine/challenge in <300 characters:\n{state['summarizer_output']}",
        generation_config={"max_output_tokens": 80}
    )
    state["critic_output"] = response.content.strip()
    return state

def consensus(state: State):
    response = state["llm"].invoke(
        f"Give balanced consensus in <=300 characters:\n"
        f"Research: {state['researcher_output']}\n"
        f"Summary: {state['summarizer_output']}\n"
        f"Critic: {state['critic_output']}",
        generation_config={"max_output_tokens": 80}
    )
    state["consensus_output"] = response.content.strip()
    return state

def run_debate(topic: str):
    """Run a debate workflow on a given topic and return results."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found in .env")

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.7, 
        google_api_key=api_key
    )

    graph = StateGraph(State)
    graph.add_node("researcher", researcher)
    graph.add_node("summarizer", summarizer)
    graph.add_node("critic", critic)
    graph.add_node("consensus", consensus)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "summarizer")
    graph.add_edge("summarizer", "critic")
    graph.add_edge("critic", "consensus")
    graph.add_edge("consensus", END)

    debate_graph = graph.compile()

    state = {"question": topic, "llm": llm}
    return debate_graph.invoke(state)
