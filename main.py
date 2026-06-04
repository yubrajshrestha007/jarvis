import argparse
import inspect
import sys

from brain import ask
from config import VOICE_ENABLED
from router import route
from tools import TOOLS

BANNER = """
Jarvis Online (llama3.1:8b)
──────────────────────────
PC control: open apps, run commands, files, volume, screenshots, Hyprland
Memory:     "my X is Y" / "what is my X?"
Chat:       ask anything (coding, Linux, study)
Voice:      python main.py --voice
Exit:       exit
"""


def call_tool(tool_name: str, args: dict):
    tool = TOOLS.get(tool_name)
    if not tool:
        return f"Unknown tool: {tool_name}"

    sig = inspect.signature(tool)
    params = sig.parameters
    accepts_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
    )

    if accepts_kwargs:
        return tool(**args)

    filtered = {k: v for k, v in args.items() if k in params}
    if filtered:
        return tool(**filtered)
    if len(params) == 0:
        return tool()
    return f"Missing arguments for {tool_name}. Expected: {list(params.keys())}"


def handle(user: str, chat_history: list) -> tuple[str, list]:
    task = route(user)
    intent = task["intent"]
    tool_name = task.get("tool")
    args = task.get("args") or {}

    if intent in ("MEMORY_WRITE", "MEMORY_READ", "SYSTEM_ACTION"):
        if not tool_name:
            return "I understood an action but no tool was selected. Try rephrasing.", chat_history
        result = call_tool(tool_name, args)
        return str(result), chat_history

    reply = ask(user, history=chat_history)
    chat_history = chat_history + [
        {"role": "user", "content": user},
        {"role": "assistant", "content": reply},
    ]
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    return reply, chat_history


def run_text_loop():
    chat_history: list = []

    while True:
        try:
            user = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user:
            continue
        if user.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break

        try:
            reply, chat_history = handle(user, chat_history)
        except Exception as e:
            reply = f"Error: {e}"

        print("\nJarvis >", reply)


def main():
    parser = argparse.ArgumentParser(description="Jarvis — local AI assistant")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Voice mode: say wake word, then command",
    )
    args = parser.parse_args()

    print(BANNER)

    use_voice = args.voice or VOICE_ENABLED

    if use_voice:
        try:
            from voice import run_voice_loop

            run_voice_loop(handle)
        except Exception as e:
            print(f"Voice failed: {e}", file=sys.stderr)
            print("Falling back to text mode.\n")
            run_text_loop()
    else:
        run_text_loop()


if __name__ == "__main__":
    main()
