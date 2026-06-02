"""
Future voice module for Jarvis.

Planned stack (when VOICE_ENABLED = True in config.py):
  - Wake word: openwakeword or Porcupine
  - STT: faster-whisper or vosk
  - TTS: piper or edge-tts
  - Loop: listen → transcribe → main.handle(user_text) → speak(reply)

Wire into main.py after text control is stable.
"""

from config import VOICE_ENABLED, WAKE_WORD


def voice_available() -> bool:
    return VOICE_ENABLED


def listen_once() -> str:
    raise NotImplementedError(
        "Voice is not enabled yet. Set VOICE_ENABLED = True in config.py "
        "and implement STT here."
    )


def speak(text: str) -> None:
    raise NotImplementedError("TTS not implemented yet.")
