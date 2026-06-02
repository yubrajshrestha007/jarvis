from router import route
from tools import TOOLS

print("Jarvis Online")

while True:

    user = input("\nYou > ")

    if user == "exit":
        break

    task = route(user)

    intent = task["intent"]
    tool_name = task.get("tool")
    args = task.get("args", {})

    if intent in ["MEMORY_WRITE", "MEMORY_READ", "SYSTEM_ACTION"]:

        tool = TOOLS.get(tool_name)

        if tool:
            result = tool(**args) if args else tool()
            print("\nJarvis >", result)

    else:
        print("\nJarvis >", "I will respond normally (chat mode)")