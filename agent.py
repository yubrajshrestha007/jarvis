from ollama import chat
import json
import re
TOOL_PROMPT = """
You are Jarvis.

You MUST use tools for memory-related questions.

Available tools:

remember_name(name)
get_name()

open_brave
open_terminal
search_web(query)

RULES:
- If user asks "what is my name", you MUST use get_name tool
- If user provides name, use remember_name tool
- NEVER answer memory questions directly
- NEVER assume user identity

Examples:

User: Open Brave
{
  "tool":"open_brave",
  "arguments":{}
}

User: Search for Hyprland plugins
{
  "tool":"search_web",
  "arguments":{
    "query":"Hyprland plugins"
  }
}

If no tool is needed:
{
  "tool":"none",
  "response":"normal answer here"
}
"""


def extract_json(text):
    """
    Extract JSON even if model adds extra text or ```json blocks
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except:
        return None


def decide(user_input):

    response = chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "system",
                "content": TOOL_PROMPT
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    text = response["message"]["content"]

    data = extract_json(text)

    if not data:
        return {
            "tool": "none",
            "response": "I couldn't understand the command."
        }

    return data