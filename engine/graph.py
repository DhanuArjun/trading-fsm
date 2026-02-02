import time
from typing_extensions import Annotated
from typing import Optional, Literal
from uuid import uuid4

from langgraph.graph import StateGraph
from langgraph.channels import LastValue, Topic

from engine.state import DecisionState, Signal
from engine.logging import log_event
from engine.llm import call_llm
from engine.memory import write_memory

MAX_RETRIES = 2

# -------------------------
# Agent A (generic)
# -------------------------
def agent_a_node(state: DecisionState):
    attempt = state["a_attempts"] + 1
    log_event(state, "agent_a_call")

    try:
        prompt = state["payload"]["agent_a_prompt"]
        data = call_llm(prompt)

        signal = {
            "recommendation": data["recommendation"],
            "confidence": float(data["confidence"]),
            "reason": data.get("reason")
        }

        log_event(state, "agent_a_result", signal)

        return {
            "agent_a": signal,
            "a_attempts": attempt,
            "trace": [f"agent_a_attempt_{attempt}"]
        }
    except Exception as e:
        log_event(state, "agent_a_failed", str(e))
        return {
            "agent_a": None,
            "a_attempts": attempt,
            "trace": [f"agent_a_failed_{attempt}"]
        }


# -------------------------
# Agent B (generic)
# -------------------------
def agent_b_node(state: DecisionState):
    attempt = state["b_attempts"] + 1
    log_event(state, "agent_b_call")

    try:
        prompt = state["payload"]["agent_b_prompt"]
        data = call_llm(prompt)

        signal = {
            "recommendation": data["recommendation"],
            "confidence": float(data["confidence"]),
            "reason": data.get("reason")
        }

        log_event(state, "agent_b_result", signal)

        return {
            "agent_b": signal,
            "b_attempts": attempt,
            "trace": [f"agent_b_attempt_{attempt}"]
        }
    except Exception as e:
        log_event(state, "agent_b_failed", str(e))
        return {
            "agent_b": None,
            "b_attempts": attempt,
            "trace": [f"agent_b_failed_{attempt}"]
        }


# -------------------------
# Human Review Node
# -------------------------
def human_review_node(state: DecisionState):
    # system pauses here
    log_event(state, "human_review_required")

    return {
        "trace": ["human_review"]
    }

# -------------------------
# Retry routers
# -------------------------
def agent_a_router(state: DecisionState):
    if state["agent_a"] is None and state["a_attempts"] <= MAX_RETRIES:
        return "RETRY"
    return "DONE"

def agent_b_router(state: DecisionState):
    if state["agent_b"] is None and state["b_attempts"] <= MAX_RETRIES:
        return "RETRY"
    return "DONE"

# -------------------------
# Policy router
# -------------------------
def policy_router(state: DecisionState):
    if state["final_recommendation"] == "REVIEW":
        return "HUMAN"
    return "DONE"

# -------------------------
# Aggregate
# -------------------------
def aggregate_node(state: DecisionState):
    a = state["agent_a"]
    b = state["agent_b"]

    if not a or not b:
        final = "REVIEW"
        conf = 0.0
    elif a["recommendation"] == b["recommendation"]:
        final = a["recommendation"]
        conf = min(a["confidence"], b["confidence"])
    else:
        final = "REVIEW"
        conf = min(a["confidence"], b["confidence"])

    log_event(state, "aggregate", {
        "final": final,
        "confidence": conf
    })

    return {
        "final_recommendation": final,
        "final_confidence": conf,
        "trace": ["aggregate"]
    }

# -------------------------
# Memory persistence
# -------------------------
def persist_memory_node(state: DecisionState):
    record = {
        "request_id": state["request_id"],
        "domain": state["domain"],
        "input": state["payload"],
        "agent_a": state["agent_a"],
        "agent_b": state["agent_b"],
        "final_recommendation": state["final_recommendation"],
        "final_confidence": state["final_confidence"],
        "human_override": state.get("human_override"),
        "timestamp": time.time()
    }
    write_memory(record)
    return {"trace": ["memory_written"]}

# -------------------------
# Graph definition
# -------------------------
graph = StateGraph(DecisionState)

graph.add_node("agent_a", agent_a_node)
graph.add_node("agent_b", agent_b_node)
graph.add_node("aggregate", aggregate_node)
graph.add_node("human", human_review_node)

graph.set_entry_point("agent_a")

graph.add_edge("agent_a", "agent_b")

graph.add_conditional_edges(
    "agent_a",
    agent_a_router,
    {"RETRY": "agent_a", "DONE": "agent_b"}
)

graph.add_conditional_edges(
    "agent_b",
    agent_b_router,
    {"RETRY": "agent_b", "DONE": "aggregate"}
)

graph.add_conditional_edges(
    "aggregate",
    policy_router,
    {
        "HUMAN": "human",
        "DONE": "__end__"
    }
)

graph.set_finish_point("aggregate")

app = graph.compile()
