from typing import TypedDict, Optional, List, Literal, Dict, Any

class Signal(TypedDict):
    recommendation: Literal["BUY", "SELL", "HOLD", "HIRE", "REJECT", "REVIEW"]
    confidence: float
    reason: Optional[str]

class DecisionState(TypedDict):
    domain: str                 # "trade", "hiring", ...
    payload: Dict[str, Any]     # domain-specific input

    agent_a: Optional[Signal]
    agent_b: Optional[Signal]

    final_recommendation: Optional[str]
    final_confidence: float

    trace: List[str]
    a_attempts: int
    b_attempts: int
    request_id: str
