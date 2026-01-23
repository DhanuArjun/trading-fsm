from typing import Optional, TypedDict, Literal, List
from langgraph.graph import StateGraph, END

# ---- State Types ----

class Signal(TypedDict):
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float

class TradeState(TypedDict):
    agent_a: Optional[Signal]
    agent_b: Optional[Signal]
    final_recommendation: Optional[Literal["BUY", "SELL", "HOLD", "REVIEW"]]
    final_confidence: float
    trace: List[str]

# ---- Nodes (stubs for now) ----

def agent_a_node(state: TradeState) -> TradeState:
    state["trace"].append("agent_a")
    # We will plug in LLM next
    state["agent_a"] = {"recommendation": "BUY", "confidence": 0.8}
    return state

def agent_b_node(state: TradeState) -> TradeState:
    state["trace"].append("agent_b")
    state["agent_b"] = {"recommendation": "HOLD", "confidence": 0.6}
    return state

def aggregate_node(state: TradeState) -> TradeState:
    state["trace"].append("aggregate")

    A = state["agent_a"]
    B = state["agent_b"]

    if not A or not B:
        state["final_recommendation"] = None
        state["final_confidence"] = 0.0
        return state

    if A["recommendation"] != B["recommendation"]:
        state["final_recommendation"] = "REVIEW"
        state["final_confidence"] = 0.0
        return state

    min_conf = min(A["confidence"], B["confidence"])
    if min_conf >= 0.7:
        state["final_recommendation"] = A["recommendation"]
        state["final_confidence"] = min_conf
    else:
        state["final_recommendation"] = "REVIEW"
        state["final_confidence"] = min_conf

    return state

def policy_node(state: TradeState):
    state["trace"].append("policy")
    return state

def policy_router(state: TradeState) -> str:
    if state["final_recommendation"] in ["BUY", "SELL", "HOLD"]:
        return "EXECUTE"
    elif state["final_recommendation"] == "REVIEW":
        return "REVIEW"
    else:
        return "FALLBACK"


# ---- Graph ----

graph = StateGraph(TradeState)

graph.add_node("agent_a", agent_a_node)
graph.add_node("agent_b", agent_b_node)
graph.add_node("aggregate", aggregate_node)
graph.add_node("policy", policy_node)

graph.set_entry_point("agent_a")

graph.add_edge("agent_a", "agent_b")
graph.add_edge("agent_b", "aggregate")
graph.add_edge("aggregate", "policy")

graph.add_conditional_edges(
    "policy",
    policy_router,
    {
        "EXECUTE": END,
        "REVIEW": END,
        "FALLBACK": END,
    },
)

app = graph.compile()
