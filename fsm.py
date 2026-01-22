from typing import TypedDict, Optional, Literal, List
import hashlib, json
from llm import llm_call

class TradeState(TypedDict):
    recommendation: Optional[Literal["BUY", "SELL", "HOLD"]]
    confidence: float
    next_action: Optional[Literal["BUY", "REVIEW", "FALLBACK"]]
    attempts: int
    trace: List[str]

def hash_state(state):
    encoded = json.dumps(state, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()[:8]

def log(node, before, after):
    print(
        f"[{node}] {hash_state(before)} → {hash_state(after)} | "
        f"confidence={after['confidence']} attempts={after['attempts']}"
    )

AUTO_ACTION_THRESHOLD = 0.7
ESCALATION_THRESHOLD = 0.5
MAX_RETRIES = 2

def policy_gate(state: TradeState) -> str:
    c = state["confidence"]
    if c >= AUTO_ACTION_THRESHOLD:
        return "BUY"
    elif c >= ESCALATION_THRESHOLD:
        return "REVIEW"
    else:
        return "FALLBACK"

def generate_signal(state: TradeState) -> TradeState:
    before = state.copy()
    print("before signal call:", before)
    attempts = state["attempts"] + 1
    trace = state["trace"] + [f"signal_attempt_{attempts}"]

    try:
        print("calling llm...")
        raw = llm_call()
        print('raw response: {raw}')
        data = json.loads(raw)
        print("data", data)

        confidence = float(data["confidence"])
        recommendation = data["recommendation"]
        print("confidence", confidence)

        if not (0 <= confidence <= 1):
            raise ValueError("bad confidence")

        new_state = {
            **state,
            "confidence": confidence,
            "recommendation": recommendation,
            "attempts": attempts,
            "trace": trace
        }

        log("signal", before, new_state)
        return new_state

    except Exception as e:
        if attempts < MAX_RETRIES:
            new_state = {**state, "attempts": attempts, "trace": trace}
            log("signal_retry", before, new_state)
            return new_state
        else:
            new_state = {**state, "confidence": 0.0, "attempts": attempts, "trace": trace}
            log("signal_fail", before, new_state)
            return new_state

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
    # Run signal until valid or retries exhausted
    while state["attempts"] < MAX_RETRIES and state["confidence"] == 0.0:
        print("Generating signal...")
        state = generate_signal(state)

    decision = policy_gate(state)
    print(f"Policy decision: {decision}")

    if decision == "BUY":
        return execute_buy(state)
    elif decision == "REVIEW":
        return human_review(state)
    else:
        return fallback(state)

state = {
    "recommendation": None,
    "confidence": 0.0,
    "next_action": None,
    "attempts": 0,
    "trace": []
}

final = run_fsm(state)
print("\nFinal State:", final)
