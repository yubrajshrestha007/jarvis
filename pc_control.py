import os
import shutil
import subprocess
from pathlib import Path

from config import COMMAND_TIMEOUT, DEFAULT_BROWSER, DEFAULT_TERMINAL, MAX_OUTPUT_CHARS


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + "\n... (output truncated)"


def run_command(command: str, timeout: int | None = None) -> str:
    """Run a shell command and return combined stdout/stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout or COMMAND_TIMEOUT,
            cwd=Path.home(),
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout or COMMAND_TIMEOUT}s."

    parts = []
    if result.stdout:
        parts.append(result.stdout)
    if result.stderr:
        parts.append(result.stderr)
    output = "".join(parts).strip()
    if not output:
        return f"Done (exit code {result.returncode})."
    return _truncate(output)


def open_app(name: str) -> str:
    """Launch an application by name or desktop entry."""
    name = name.strip()
    if shutil.which(name):
        subprocess.Popen([name], start_new_session=True)
        return f"Launched {name}."

    try:
        subprocess.Popen(
            ["gtk-launch", name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return f"Launched {name}."
    except FileNotFoundError:
        pass

    return f"Could not find app: {name}"


def open_url(url: str) -> str:
    subprocess.Popen(
        [DEFAULT_BROWSER, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return f"Opening {url}"


def open_file(path: str) -> str:
    path = os.path.expanduser(path)
    subprocess.Popen(["xdg-open", path], start_new_session=True)
    return f"Opened {path}"


def open_terminal(command: str | None = None) -> str:
    if command:
        subprocess.Popen([DEFAULT_TERMINAL, "-e", command], start_new_session=True)
        return f"Running in {DEFAULT_TERMINAL}: {command}"
    subprocess.Popen([DEFAULT_TERMINAL], start_new_session=True)
    return f"Opened {DEFAULT_TERMINAL}."


def open_brave() -> str:
    return open_app(DEFAULT_BROWSER)


def list_dir(path: str = ".") -> str:
    target = Path(os.path.expanduser(path))
    if not target.exists():
        return f"Path not found: {path}"
    if not target.is_dir():
        return f"Not a directory: {path}"

    entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    lines = []
    for entry in entries[:200]:
        prefix = "d" if entry.is_dir() else "-"
        lines.append(f"{prefix} {entry.name}")
    if len(entries) > 200:
        lines.append(f"... and {len(entries) - 200} more")
    return "\n".join(lines) or "(empty directory)"


def disk_usage() -> str:
    import psutil

    lines = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        lines.append(
            f"{part.mountpoint}: {usage.percent}% used "
            f"({usage.used // (1024**3)}G / {usage.total // (1024**3)}G)"
        )
    return "\n".join(lines) or "No disk info available."


def notify(message: str) -> str:
    subprocess.Popen(
        ["notify-send", "Jarvis", message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return "Notification sent."


def screenshot(path: str = "~/Pictures/jarvis-screenshot.png") -> str:
    path = os.path.expanduser(path)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    if shutil.which("grim"):
        subprocess.run(["grim", path], check=True)
        return f"Screenshot saved to {path}"

    if shutil.which("scrot"):
        subprocess.run(["scrot", path], check=True)
        return f"Screenshot saved to {path}"

    return "No screenshot tool found (install grim or scrot)."


def volume_set(level: int) -> str:
    level = max(0, min(100, int(level)))
    if shutil.which("wpctl"):
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{level}%"])
        return f"Volume set to {level}%."
    if shutil.which("pamixer"):
        subprocess.run(["pamixer", "--set-volume", str(level)])
        return f"Volume set to {level}%."
    return "No volume tool found (install wireplumber/wpctl or pamixer)."


def volume_mute() -> str:
    if shutil.which("wpctl"):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        return "Toggled mute."
    if shutil.which("pamixer"):
        subprocess.run(["pamixer", "-t"])
        return "Toggled mute."
    return "No volume tool found."


def clipboard_write(text: str) -> str:
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text, text=True, check=True)
        return "Copied to clipboard."
    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text,
            text=True,
            check=True,
        )
        return "Copied to clipboard."
    return "No clipboard tool found (install wl-clipboard or xclip)."


def hypr_command(action: str) -> str:
    """Run a hyprctl command (Hyprland window/workspace control)."""
    if not shutil.which("hyprctl"):
        return "hyprctl not found (not on Hyprland?)."
    result = subprocess.run(
        ["hyprctl", *action.split()],
        capture_output=True,
        text=True,
    )
    out = (result.stdout or result.stderr or "").strip()
    return _truncate(out) if out else "Done."
