def agent_a_prompt(symbol: str):
    return f"""
You are an optimistic trading analyst.

Analyze stock {symbol} based on general market trends.
Return JSON:

{{
  "recommendation": "BUY | SELL | HOLD",
  "confidence": number between 0 and 1,
  "reason": "short text"
}}
"""


def agent_b_prompt(symbol: str):
    return f"""
You are a pessimistic trading analyst.

Analyze risks for stock {symbol}.
Return JSON:

{{
  "recommendation": "BUY | SELL | HOLD",
  "confidence": number between 0 and 1,
  "reason": "short text"
}}
"""
