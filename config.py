MODEL_NAME = "llama3.1:8b"

# Apps (match memory.json defaults; override here if needed)
DEFAULT_TERMINAL = "kitty"
DEFAULT_BROWSER = "brave"

# Shell commands via run_command
COMMAND_TIMEOUT = 60
MAX_OUTPUT_CHARS = 8000

# Voice (run: python main.py --voice)
VOICE_ENABLED = False
WAKE_WORD = "jarvis"
# Small English model (~40 MB). Auto-downloaded on first run if missing.
VOSK_MODEL_DIR = "~/.local/share/jarvis/vosk-model-small-en-us-0.15"
VOSK_MODEL_URL = (
    "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
)
SAMPLE_RATE = 16000
COMMAND_MAX_SECONDS = 12
SILENCE_SECONDS = 1.2
TTS_MAX_CHARS = 400
# edge-tts voice (needs network). Falls back to espeak-ng if offline.
EDGE_TTS_VOICE = "en-GB-RyanNeural"

SYSTEM_PROMPT = """
You are Jarvis.

You are Yubraj's personal AI assistant.

You help with:
- Linux administration
- Programming
- AI development
- Study and productivity
- Controlling the PC (apps, terminal, files, system info)

Be concise, accurate and practical.
When the user asks you to do something on the computer, they should phrase it as an action
(e.g. "open neovim", "list files in Downloads") — the router will run the right tool.
For explanations and coding help, answer normally.
Keep spoken answers short when possible.
"""
