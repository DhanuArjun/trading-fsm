from graph import app

initial_state = {
    "agent_a": None,
    "agent_b": None,
    "final_recommendation": None,
    "final_confidence": 0.0,
    "trace": []
}

result = app.invoke(initial_state)
print(result)
