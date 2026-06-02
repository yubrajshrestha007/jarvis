from ollama import chat
import json

ROUTER_PROMPT = """
You are an intent router for an AI assistant.

Return ONLY JSON.

Possible intents:

1. MEMORY_WRITE
2. MEMORY_READ
3. SYSTEM_ACTION
4. CHAT

TOOLS:

- set_fact(key, value)
- get_fact(key)
- open_brave()
- open_terminal(command)
- ram_usage()
- cpu_usage()

RULES:
- If user stores info → MEMORY_WRITE
- If user asks "what is X" → MEMORY_READ
- If system task → SYSTEM_ACTION
- Else → CHAT

OUTPUT FORMAT:

{
  "intent": "",
  "tool": "",
  "args": {}
}
"""

def route(user_input):
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    return json.loads(response["message"]["content"])