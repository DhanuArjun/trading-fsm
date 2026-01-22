# Trading FSM — Multi-Agent AI Control System

This repository demonstrates how to run multiple LLM agents in production **without letting any single model control outcomes**.

Instead of trusting one AI, this system uses:
- independent agents
- explicit consensus rules
- deterministic policy gates
- safe fallbacks

to ensure that **AI can fail without the system breaking**.

This is not a chatbot.
This is an **AI control plane**.

---

## What problem this solves

Large Language Models are:
- probabilistic
- inconsistent
- sometimes wrong
- sometimes unavailable
- sometimes refusing to answer

Yet many AI applications allow the model to directly decide actions.

That is unsafe.

This project shows how to treat LLMs like **unreliable sensors**, not decision makers.

---

## System Architecture

        ┌─────────────────┐
        │  Agent A (LLM)  │Optimistic analyst
        └─────────────────┘
                │
                │
Start → Signal Fan-out → Aggregate → Policy Gate → Action
                │
        ┌─────────────────┐
        │ Agent B (LLM)   │Conservative analyst
        └─────────────────┘

Each agent:
- calls a real LLM
- outputs structured JSON
- can fail, refuse, or return garbage
- is retried and validated independently

The **system** (not the AI) decides what to do.

---

## Agents

Two independent AI agents analyze the same trading scenario:

| Agent | Role |
|------|------|
| Agent-A | Optimistic analyst (seeks opportunity) |
| Agent-B | Conservative analyst (seeks risk) |

They are deliberately given different prompts to **force disagreement**.

Each returns:

```json
{
  "recommendation": "BUY | SELL | HOLD",
  "confidence": 0.0–1.0
}
```

## Aggregation (No AI here)

Each agent:
- If either agent is missing → FALLBACK
- If agents disagree → REVIEW
- If both agree and min(confidence) ≥ 0.7 → accept
- Otherwise → REVIEW

This prevents:
- hallucinated confidence
- single-model failure
- unsafe autonomous action

## Policy Gate (No AI here)

final_recommendation = BUY | SELL | HOLD | REVIEW | FALLBACK

## Running
```python fsm.py```