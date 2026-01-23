from fastapi import FastAPI
from pydantic import BaseModel
from graph import app as graph_app
from uuid import uuid4

app = FastAPI(title="Trading AI Control Plane")

class TradeRequest(BaseModel):
    symbol: str

class TradeResponse(BaseModel):
    agent_a: dict | None
    agent_b: dict | None
    final_recommendation: str | None
    final_confidence: float
    trace: list[str]

@app.post("/trade", response_model=TradeResponse)
def trade(req: TradeRequest):
    state = {
        "agent_a": None,
        "agent_b": None,
        "final_recommendation": None,
        "final_confidence": 0.0,
        "trace": [],
        "a_attempts": 0,
        "b_attempts": 0,
        "request_id": str(uuid4())
    }

    result = graph_app.invoke(state)

    return result
