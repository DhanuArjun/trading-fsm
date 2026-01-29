def agent_a_prompt(candidate_profile: str):
    return f"""
You are an optimistic hiring manager.

Evaluate the following candidate:

{candidate_profile}

Return JSON:

{{
  "recommendation": "HIRE | HOLD | REJECT",
  "confidence": number between 0 and 1,
  "reason": "short text"
}}
"""


def agent_b_prompt(candidate_profile: str):
    return f"""
You are a skeptical HR reviewer.

Find risks and weaknesses in this candidate:

{candidate_profile}

Return JSON:

{{
  "recommendation": "HIRE | HOLD | REJECT",
  "confidence": number between 0 and 1,
  "reason": "short text"
}}
"""
