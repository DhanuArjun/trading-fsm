from engine.graph import app
from engine.state import DecisionState
from domains.trading.prompts import agent_a_prompt, agent_b_prompt


def run_trading_decision(symbol: str):
    state: DecisionState = {
        "request_id": str(symbol),
        "payload": {
            "agent_a_prompt": agent_a_prompt(symbol),
            "agent_b_prompt": agent_b_prompt(symbol),
        },
        "agent_a": None,
        "agent_b": None,
        "final_recommendation": None,
        "final_confidence": 0.0,
        "trace": [],
        "a_attempts": 0,
        "b_attempts": 0,
    }

    result = app.invoke(state)
    return result
