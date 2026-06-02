import inspect

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
    # Keep last 10 turns to stay within context
    if len(chat_history) > 20:
        chat_history = chat_history[-20:]
    return reply, chat_history


def main():
    print(BANNER)
    if VOICE_ENABLED:
        print("Voice mode: enabled (see voice.py)")
    else:
        print("Voice mode: off (enable later in config.py)")

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


if __name__ == "__main__":
    main()
