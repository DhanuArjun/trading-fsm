from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def llm_call():
    print("Inside llm_call")
    print("API", os.getenv("OPENAI_API_KEY"))
    prompt = """
    You are a trading analyst.
    Given stock TMCV and Q1 results,
    output JSON only in this format:

    {
      "recommendation": "BUY | SELL | HOLD",
      "confidence": number between 0 and 1,
      "reason": "short text"
    }
    """

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    print('resp', resp)

    return resp.choices[0].message.content

