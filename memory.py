import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")


def load_memory():
    if not MEMORY_FILE.exists():
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def set_memory(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)
    return f"Stored {key} = {value}"


def get_memory(key):
    data = load_memory()
    return data.get(key, None)