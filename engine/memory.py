import json
import time

MEMORY_FILE = "memory.jsonl"

def write_memory(record):
    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

def load_memory(domain=None, limit=20):
    records = []
    try:
        with open(MEMORY_FILE, "r") as f:
            for line in f:
                r = json.loads(line)
                if domain is None or r["domain"] == domain:
                    records.append(r)
    except FileNotFoundError:
        pass
    return records[-limit:]
