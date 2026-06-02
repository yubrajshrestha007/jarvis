from ollama import chat
from memory import load_memory
from config import MODEL_NAME, SYSTEM_PROMPT


def ask(user_input: str):

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

{memory_context}
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response["message"]["content"]