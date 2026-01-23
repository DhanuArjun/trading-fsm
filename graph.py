from typing import Optional, TypedDict, Literal, List
from langgraph.graph import StateGraph, END
from llm import call_llm, agent_a_prompt, agent_b_prompt
from typing_extensions import Annotated
from langgraph.channels import LastValue, Topic

# ---- State Types ----

class Signal(TypedDict):
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float

class TradeState(TypedDict):
    agent_a: Annotated[Optional[Signal], LastValue(Signal)]
    agent_b: Annotated[Optional[Signal], LastValue(Signal)]
    final_recommendation: Optional[Literal["BUY", "SELL", "HOLD", "REVIEW"]]
    final_confidence: float
    trace: Annotated[List[str], Topic(list)]

# ---- Nodes (LLM inside) ----

def agent_a_node(state: TradeState):
    try:
        data = call_llm(agent_a_prompt("TMPV"))
        return {
            "agent_a": {
                "recommendation": data["recommendation"],
                "confidence": float(data["confidence"])
            },
            "trace": ["agent_a"]
        }
    except Exception:
        return {
            "agent_a": None,
            "trace": ["agent_b"]
        }

def agent_b_node(state: TradeState):
    try:
        data = call_llm(agent_b_prompt("TMPV"))
        return {
            "agent_b": {
                "recommendation": data["recommendation"],
                "confidence": float(data["confidence"])
            },
            "trace": state["trace"] + ["agent_b"]
        }
    except Exception:
        return {
            "agent_b": None,
            "trace": state["trace"] + ["agent_b_failed"]
        }

def aggregate_node(state: TradeState):
    A = state["agent_a"]
    B = state["agent_b"]

    trace = state["trace"] + ["aggregate"]

    if not A or not B:
        return {
            "final_recommendation": None,
            "final_confidence": 0.0,
            "trace": trace
        }

    if A["recommendation"] != B["recommendation"]:
        return {
            "final_recommendation": "REVIEW",
            "final_confidence": 0.0,
            "trace": trace
        }

    min_conf = min(A["confidence"], B["confidence"])

    if min_conf >= 0.7:
        return {
            "final_recommendation": A["recommendation"],
            "final_confidence": min_conf,
            "trace": trace
        }
    else:
        return {
            "final_recommendation": "REVIEW",
            "final_confidence": min_conf,
            "trace": trace
        }

def policy_node(state: TradeState):
    return {
        "trace": state["trace"] + ["policy"]
    }

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

graph.set_entry_point("fanout")

def fanout_node(state):
    return {
        "trace": ["fanout"]
    }

graph.add_node("fanout", fanout_node)

graph.add_edge("fanout", "agent_a")
graph.add_edge("fanout", "agent_b")

graph.add_edge("agent_a", "aggregate")
graph.add_edge("agent_b", "aggregate")


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
