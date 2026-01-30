from typing import TypedDict, Optional, List, Literal, Dict, Any

class Signal(TypedDict):
    recommendation: Literal["BUY", "SELL", "HOLD", "HIRE", "REJECT", "REVIEW"]
    confidence: float
    reason: Optional[str]

class DecisionState(TypedDict):
    domain: str
    payload: dict

    agent_a: Optional[Signal]
    agent_b: Optional[Signal]

    final_recommendation: Optional[str]
    final_confidence: float

    human_override: Optional[str]
    human_reason: Optional[str]

    trace: List[str]
    a_attempts: int
    b_attempts: int
    request_id: str
