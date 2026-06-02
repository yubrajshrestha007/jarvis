import subprocess
import psutil
from memory import set_memory, get_memory


# ---------------- MEMORY TOOLS ----------------

def set_fact(key, value):
    return set_memory(key, value)


def get_fact(key):
    value = get_memory(key)
    if value is None:
        return f"No stored value for {key}"
    return f"{key} = {value}"


# ---------------- SYSTEM TOOLS ----------------

def ram_usage():
    mem = psutil.virtual_memory()
    return f"RAM used: {mem.percent}%"


def cpu_usage():
    return f"CPU usage: {psutil.cpu_percent()}%"


def open_brave():
    subprocess.Popen(["brave"])
    return "Opening Brave"


def open_terminal(command=None):
    if command:
        subprocess.Popen(["kitty", "-e", command])
        return f"Running {command} in terminal"

    subprocess.Popen(["kitty"])
    return "Opening terminal"


# ---------------- TOOL REGISTRY ----------------

TOOLS = {
    "set_fact": set_fact,
    "get_fact": get_fact,
    "ram_usage": ram_usage,
    "cpu_usage": cpu_usage,
    "open_brave": open_brave,
    "open_terminal": open_terminal,
}