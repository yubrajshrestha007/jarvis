import psutil

from memory import get_memory, set_memory
from pc_control import (
    clipboard_write,
    disk_usage,
    hypr_command,
    list_dir,
    notify,
    open_app,
    open_brave,
    open_file,
    open_terminal,
    open_url,
    run_command,
    screenshot,
    volume_mute,
    volume_set,
)


# ---------------- MEMORY ----------------

def set_fact(key, value):
    return set_memory(key, value)


def get_fact(key):
    value = get_memory(key)
    if value is None:
        return f"No stored value for {key}"
    return f"{key} = {value}"


# ---------------- SYSTEM INFO ----------------

def ram_usage():
    mem = psutil.virtual_memory()
    return f"RAM: {mem.percent}% used ({mem.used // (1024**3)}G / {mem.total // (1024**3)}G)"


def cpu_usage():
    return f"CPU: {psutil.cpu_percent(interval=0.5)}%"


def battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected (desktop or driver missing)."
    status = "charging" if battery.power_plugged else "on battery"
    return f"Battery: {battery.percent}% ({status})"


# ---------------- TOOL REGISTRY ----------------

TOOLS = {
    # memory
    "set_fact": set_fact,
    "get_fact": get_fact,
    # system info
    "ram_usage": ram_usage,
    "cpu_usage": cpu_usage,
    "disk_usage": disk_usage,
    "battery_status": battery_status,
    # PC control
    "run_command": run_command,
    "open_app": open_app,
    "open_url": open_url,
    "open_file": open_file,
    "open_brave": open_brave,
    "open_terminal": open_terminal,
    "list_dir": list_dir,
    "notify": notify,
    "screenshot": screenshot,
    "volume_set": volume_set,
    "volume_mute": volume_mute,
    "clipboard_write": clipboard_write,
    "hypr_command": hypr_command,
}
