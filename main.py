from agent import decide
from tools import TOOLS

print("Jarvis Online")

while True:

    user = input("\nYou > ")

    if user.lower() in ["exit", "quit"]:
        break

    decision = decide(user)

    tool_name = decision.get("tool")

    if tool_name == "none":
        print("\nJarvis >", decision.get("response"))
        continue

    tool = TOOLS.get(tool_name)

    if not tool:
        print("Unknown tool:", tool_name)
        continue

    try:
        args = decision.get("arguments", {})
        result = tool(**args)
        print("\nJarvis >", result)

    except Exception as e:
        print("Tool error:", e)