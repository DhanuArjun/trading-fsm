import uuid
from engine.graph import app
from engine.state import DecisionState
from domains.hiring.prompts import agent_a_prompt, agent_b_prompt


def run_hiring_decision(candidate_profile: str):
    state: DecisionState = {
        "request_id": str(uuid.uuid4()),
        "domain": "hiring",
        "payload": {
            "agent_a_prompt": agent_a_prompt(candidate_profile),
            "agent_b_prompt": agent_b_prompt(candidate_profile),
        },
        "agent_a": None,
        "agent_b": None,
        "final_recommendation": None,
        "final_confidence": 0.0,
        "trace": [],
        "a_attempts": 0,
        "b_attempts": 0,
    }

    return app.invoke(state)
