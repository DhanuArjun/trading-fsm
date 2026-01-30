from fastapi import FastAPI
from pydantic import BaseModel
from domains.trading.service import run_trading_decision
from domains.hiring.service import run_hiring_decision

app = FastAPI()

class TradeRequest(BaseModel):
    symbol: str

class HiringRequest(BaseModel):
    candidate_profile: str

class HumanOverride(BaseModel):
    request_id: str
    decision: str
    reason: str
pending_reviews = {}

@app.post("/trade")
def trade(req: TradeRequest):
    return run_trading_decision(req.symbol)


@app.post("/hiring")
def hiring(req: HiringRequest):
    return run_hiring_decision(req.candidate_profile)


@app.post("/human/override")
def human_override(req: HumanOverride):
    state = pending_reviews.pop(req.request_id)

    state["human_override"] = req.decision
    state["human_reason"] = req.reason
    state["final_recommendation"] = req.decision

    return state