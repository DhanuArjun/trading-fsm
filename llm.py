import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = resp.choices[0].message.content

    # strip markdown fences
    raw = raw.strip()
    raw = re.sub(r"^```json", "", raw)
    raw = re.sub(r"```$", "", raw)
    raw = raw.strip()

    return json.loads(raw)

def agent_a_prompt(symbol: str):
    return f"""
You are an optimistic trading analyst.
You MUST always return JSON.
If uncertain, lower confidence.

Given stock {symbol} and recent results,
output:

{{
  "recommendation": "BUY | SELL | HOLD",
  "confidence": number between 0 and 1
}}
"""

def agent_b_prompt(symbol: str):
    return f"""
You are a conservative risk analyst.
You MUST always return JSON.
If uncertain, lower confidence.

Given stock {symbol} and recent results,
output:

{{
  "recommendation": "BUY | SELL | HOLD",
  "confidence": number between 0 and 1
}}
"""
