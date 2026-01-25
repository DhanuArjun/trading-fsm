import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = resp.choices[0].message.content

    # strip markdown if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)
