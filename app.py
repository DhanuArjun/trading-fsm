from fastapi import FastAPI
from pydantic import BaseModel
from domains.trading.service import run_trading_decision
from domains.hiring.service import run_hiring_decision

app = FastAPI()

class TradeRequest(BaseModel):
    symbol: str

class HiringRequest(BaseModel):
    candidate_profile: str


@app.post("/trade")
def trade(req: TradeRequest):
    return run_trading_decision(req.symbol)


@app.post("/hiring")
def hiring(req: HiringRequest):
    return run_hiring_decision(req.candidate_profile)
