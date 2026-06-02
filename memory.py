import json
from pathlib import Path

FILE = Path("memory.json")


def load_memory():
    if not FILE.exists():
        return {}
    return json.loads(FILE.read_text())


def save_memory(data):
    FILE.write_text(json.dumps(data, indent=2))


def set_memory(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)
    return f"Stored {key} = {value}"


def get_memory(key):
    data = load_memory()
    return data.get(key)