from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt):
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content

def llm_call_agent_a():
    prompt = """
    You are an optimistic trading analyst.
    You MUST always return JSON, even if data is incomplete.
    If uncertain, set confidence low.

    Given stock TMPV and Q1 results,
    output JSON only:

    {
      "recommendation": "BUY | SELL | HOLD",
      "confidence": number between 0 and 1
    }
    """
    return call_llm(prompt)

def llm_call_agent_b():
    prompt = """
    You are a conservative risk analyst.
    You MUST always return JSON, even if data is incomplete.
    If uncertain, set confidence low.

    Given stock TMPV and Q1 results,
    output JSON only:

    {
      "recommendation": "BUY | SELL | HOLD",
      "confidence": number between 0 and 1
    }
    """
    return call_llm(prompt)
