from ollama import chat

from config import MODEL_NAME, SYSTEM_PROMPT
from memory import load_memory


def ask(user_input: str, history: list | None = None) -> str:
    memory = load_memory()

    if memory:
        memory_context = "Known user information:\n"
        for k, v in memory.items():
            memory_context += f"- {k}: {v}\n"
    else:
        memory_context = "No stored user information."

    system_message = f"""
{SYSTEM_PROMPT}

IMPORTANT RULES:
- Use the stored user information when answering
- Never ignore memory if it exists
- Do not guess user identity
- You cannot run shell commands yourself; tell the user to ask you to "run ..." for actions

{memory_context}
"""

    messages = [{"role": "system", "content": system_message}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    response = chat(model=MODEL_NAME, messages=messages)
    return response["message"]["content"]
