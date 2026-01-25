import json

def log_event(state, event, payload=None):
    print(json.dumps({
        "request_id": state["request_id"],
        "event": event,
        "a_attempts": state["a_attempts"],
        "b_attempts": state["b_attempts"],
        "domain": state["domain"],
        "payload": payload
    }))
