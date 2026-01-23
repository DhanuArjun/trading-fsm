from typing import TypedDict, Optional, Literal, List
import hashlib, json
import re
from llm import llm_call_agent_a, llm_call_agent_b

class TradeState(TypedDict):
    agent_a: Optional[dict]
    agent_b: Optional[dict]
    final_recommendation: Optional[str]
    final_confidence: float
    next_action: Optional[str]
    attempts_a: int
    attempts_b: int
    trace: list[str]

def hash_state(state):
    encoded = json.dumps(state, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()[:8]

def extract_json(raw):
    # remove markdown fences
    raw = raw.strip()
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"```$", "", raw)
    raw = raw.strip()
    return json.loads(raw)

def log(node, before, after):
    def safe(d, k):
        return d[k] if k in d else None

    print(
        f"[{node}] {hash_state(before)} → {hash_state(after)} | "
        f"A={safe(after,'agent_a')} "
        f"B={safe(after,'agent_b')} "
        f"final={safe(after,'final_recommendation')} "
        f"conf={safe(after,'final_confidence')} "
        f"a_try={safe(after,'attempts_a')} "
        f"b_try={safe(after,'attempts_b')}"
    )

AUTO_ACTION_THRESHOLD = 0.7
ESCALATION_THRESHOLD = 0.5
MAX_RETRIES = 2

def aggregate(state):
    before = state.copy()
    A = state["agent_a"]
    B = state["agent_b"]

    if not A or not B:
        new = {**state, "final_recommendation": None, "final_confidence": 0.0}
        log("aggregate_missing", before, new)
        return new

    if A["recommendation"] != B["recommendation"]:
        new = {**state, "final_recommendation": "REVIEW", "final_confidence": 0.0}
        log("aggregate_disagree", before, new)
        return new

    min_conf = min(A["confidence"], B["confidence"])

    if min_conf >= 0.7:
        new = {**state, "final_recommendation": A["recommendation"], "final_confidence": min_conf}
        log("aggregate_consensus", before, new)
        return new
    else:
        new = {**state, "final_recommendation": "REVIEW", "final_confidence": min_conf}
        log("aggregate_weak", before, new)
        return new


def policy_gate(state):
    if state["final_recommendation"] in ["BUY", "SELL", "HOLD"]:
        return state["final_recommendation"]
    elif state["final_recommendation"] == "REVIEW":
        return "REVIEW"
    else:
        return "FALLBACK"


def agent_a_signal(state):
    before = state.copy()
    attempts = state["attempts_a"] + 1
    trace = state["trace"] + [f"A_attempt_{attempts}"]

    try:
        raw = llm_call_agent_a()
        print("AGENT A RAW:", repr(raw))
        data = extract_json(raw)

        rec = data["recommendation"]
        conf = float(data["confidence"])
        if rec not in ["BUY", "SELL", "HOLD"]:
            raise ValueError("bad recommendation")
        
        if not (0 <= conf <= 1):
            raise ValueError("bad confidence")

        new = {**state, "agent_a": {"recommendation": rec, "confidence": conf},
               "attempts_a": attempts, "trace": trace}
        log("agent_a", before, new)
        return new

    except Exception:
        if attempts < MAX_RETRIES:
            new = {**state, "attempts_a": attempts, "trace": trace}
            log("agent_a_retry", before, new)
            return new
        else:
            new = {**state, "agent_a": None, "attempts_a": attempts, "trace": trace}
            log("agent_a_fail", before, new)
            return new

def agent_b_signal(state):
    before = state.copy()
    attempts = state["attempts_b"] + 1
    trace = state["trace"] + [f"B_attempt_{attempts}"]

    try:
        raw = llm_call_agent_b()
        print("AGENT B RAW:", repr(raw))

        data = extract_json(raw)
        print("AGENT B PARSED:", data)

        rec = data.get("recommendation")
        conf = data.get("confidence")

        print("AGENT B FIELDS:", rec, conf)

        if rec not in ["BUY", "SELL", "HOLD"]:
            raise ValueError(f"bad recommendation {rec}")

        conf = float(conf)
        if not (0.0 <= conf <= 1.0):
            raise ValueError(f"bad confidence {conf}")

        new = {
            **state,
            "agent_b": {"recommendation": rec, "confidence": conf},
            "attempts_b": attempts,
            "trace": trace
        }

        log("agent_b", before, new)
        return new

    except Exception:
        if attempts < MAX_RETRIES:
            new = {**state, "attempts_b": attempts, "trace": trace}
            log("agent_b_retry", before, new)
            return new
        else:
            new = {**state, "agent_b": None, "attempts_b": attempts, "trace": trace}
            log("agent_b_fail", before, new)
            return new

def execute_buy(state):
    before = state.copy()
    new = {**state, "next_action": "BUY"}
    log("BUY", before, new)
    return new

def human_review(state):
    before = state.copy()
    new = {**state, "next_action": "REVIEW"}
    log("REVIEW", before, new)
    return new

def fallback(state):
    before = state.copy()
    new = {**state, "next_action": "FALLBACK"}
    log("FALLBACK", before, new)
    return new

def run_fsm(state: TradeState):

    decision = policy_gate(state)
    print(f"Policy decision: {decision}")

    if decision == "BUY":
        return execute_buy(state)
    elif decision == "REVIEW":
        return human_review(state)
    else:
        return fallback(state)

state = {
    "agent_a": None,
    "agent_b": None,
    "final_recommendation": None,
    "final_confidence": 0.0,
    "next_action": None,
    "attempts_a": 0,
    "attempts_b": 0,
    "trace": []
}

state = agent_a_signal(state)
state = agent_b_signal(state)
state = aggregate(state)

decision = policy_gate(state)

print("Policy:", decision)