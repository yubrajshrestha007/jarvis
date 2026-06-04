"""
Voice mode: wake word → speech-to-text → Jarvis → text-to-speech.

Dependencies (pip): vosk, sounddevice
System (Arch):       sudo pacman -S portaudio espeak-ng
Optional TTS:        edge-tts (uses network + mpv for playback)
"""

from __future__ import annotations

import json
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from config import (
    COMMAND_MAX_SECONDS,
    EDGE_TTS_VOICE,
    SAMPLE_RATE,
    SILENCE_SECONDS,
    TTS_MAX_CHARS,
    VOSK_MODEL_DIR,
    VOSK_MODEL_URL,
    WAKE_WORD,
)

EXIT_PHRASES = {"exit", "quit", "goodbye", "bye", "stop"}


def _missing_packages() -> list[str]:
    missing = []
    try:
        import sounddevice  # noqa: F401
    except ImportError:
        missing.append("sounddevice")
    try:
        from vosk import Model  # noqa: F401
    except ImportError:
        missing.append("vosk")
    return missing


def ensure_voice_deps() -> None:
    missing = _missing_packages()
    if missing:
        raise RuntimeError(
            "Voice dependencies missing. Install with:\n"
            "  pip install vosk sounddevice\n"
            "  sudo pacman -S portaudio espeak-ng\n"
            f"Missing: {', '.join(missing)}"
        )


def model_path() -> Path:
    return Path(VOSK_MODEL_DIR).expanduser()


def download_vosk_model(target: Path | None = None) -> Path:
    target = target or model_path()
    if (target / "am").exists() or (target / "graph").exists():
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    zip_path = target.parent / "vosk-model.zip"

    print(f"Downloading Vosk model (~40 MB) to {target}...")
    with urllib.request.urlopen(VOSK_MODEL_URL, timeout=120) as resp:
        zip_path.write_bytes(resp.read())

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target.parent)

    zip_path.unlink(missing_ok=True)

    extracted = next(target.parent.glob("vosk-model-*"), None)
    if extracted and extracted != target:
        if target.exists():
            shutil.rmtree(target)
        extracted.rename(target)

    print("Model ready.")
    return target


def load_vosk_model():
    from vosk import Model

    path = model_path()
    if not path.exists():
        download_vosk_model(path)
    return Model(str(path))


def _strip_wake_word(text: str, wake: str = WAKE_WORD) -> str:
    pattern = re.compile(rf"\b{re.escape(wake)}\b", re.IGNORECASE)
    cleaned = pattern.sub("", text).strip(" ,.-")
    return cleaned or text.strip()


def _device_supports_samplerate(device: int, samplerate: int = SAMPLE_RATE) -> bool:
    import sounddevice as sd

    try:
        sd.check_input_settings(device=device, samplerate=samplerate, channels=1)
        return True
    except Exception:
        return False


def _select_input_device():
    import sounddevice as sd

    device = sd.default.device
    if isinstance(device, (tuple, list)) and device:
        try:
            if (
                sd.query_devices(device[0])["max_input_channels"] > 0
                and _device_supports_samplerate(device[0])
            ):
                return device[0]
        except Exception:
            pass
    if isinstance(device, int):
        try:
            if (
                sd.query_devices(device)["max_input_channels"] > 0
                and _device_supports_samplerate(device)
            ):
                return device
        except Exception:
            pass

    fallback = None
    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] <= 0:
            continue
        if fallback is None:
            fallback = idx
        if _device_supports_samplerate(idx):
            print(f"Using input device {idx}: {dev['name']}")
            return idx

    if fallback is not None:
        dev = sd.query_devices(fallback)
        print(
            f"No device supports {SAMPLE_RATE}Hz mono. "
            f"Falling back to device {fallback}: {dev['name']}"
        )
        return fallback

    return None


def _audio_stream():
    import sounddevice as sd

    audio_q: queue.Queue[bytes] = queue.Queue()
    device = _select_input_device()
    if device is None:
        raise RuntimeError("No input audio device found.")

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_q.put(bytes(indata))

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
        device=device,
    )
    return stream, audio_q


def _listen(
    model,
    *,
    until_silence: bool = False,
    max_seconds: float = COMMAND_MAX_SECONDS,
    wake_only: bool = False,
) -> str:
    from vosk import KaldiRecognizer

    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)
    wake = WAKE_WORD.lower()

    stream, audio_q = _audio_stream()
    parts: list[str] = []
    last_voice = time.time()
    start = time.time()

    with stream:
        while True:
            if time.time() - start > max_seconds:
                break

            try:
                data = audio_q.get(timeout=0.2)
            except queue.Empty:
                if until_silence and parts and time.time() - last_voice > SILENCE_SECONDS:
                    break
                continue

            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "").strip()
                if text:
                    parts.append(text)
                    last_voice = time.time()
                    if wake_only and wake in text.lower():
                        return text
            else:
                partial = json.loads(rec.PartialResult()).get("partial", "").strip()
                if partial:
                    last_voice = time.time()
                    if wake_only and wake in partial.lower():
                        return partial

    return " ".join(parts).strip()


def wait_for_wake_word(model) -> bool:
    print(f'\n🔊 Waiting for "{WAKE_WORD}"...')
    while True:
        heard = _listen(model, wake_only=True, max_seconds=60)
        if heard and WAKE_WORD.lower() in heard.lower():
            print("Wake word detected.")
            return True


def listen_command(model) -> str:
    print("🎤 Listening...")
    text = _listen(model, until_silence=True, max_seconds=COMMAND_MAX_SECONDS)
    print(f'Heard: "{text}"' if text else "Heard: (nothing)")
    return _strip_wake_word(text)


def speak(text: str) -> None:
    if not text:
        return

    spoken = text.strip()
    if len(spoken) > TTS_MAX_CHARS:
        spoken = spoken[:TTS_MAX_CHARS].rsplit(" ", 1)[0] + "..."

    if _speak_espeak(spoken):
        return
    if _speak_edge(spoken):
        return

    print("(No TTS available — install espeak-ng or: pip install edge-tts)")


def _speak_espeak(text: str) -> bool:
    for cmd in ("espeak-ng", "espeak"):
        if shutil.which(cmd):
            subprocess.run(
                [cmd, "-s", "165", "-a", "120", text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            return True
    return False


def _speak_edge(text: str) -> bool:
    if not shutil.which("mpv"):
        return False
    try:
        import edge_tts
    except ImportError:
        return False

    async def _generate(path: Path):
        communicate = edge_tts.Communicate(text, EDGE_TTS_VOICE)
        await communicate.save(str(path))

    import asyncio

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        mp3 = Path(f.name)

    try:
        asyncio.run(_generate(mp3))
        subprocess.run(
            ["mpv", "--no-video", "--really-quiet", str(mp3)],
            check=False,
        )
        return True
    except Exception:
        return False
    finally:
        mp3.unlink(missing_ok=True)


def run_voice_loop(handle_fn) -> None:
    """handle_fn(user_text) -> reply string"""
    ensure_voice_deps()
    model = load_vosk_model()
    chat_history: list = []

    print("Voice mode active. Ctrl+C to stop.")
    print(f'Say "{WAKE_WORD}" then your command. Say "exit" to quit.')

    while True:
        try:
            wait_for_wake_word(model)
            user_text = listen_command(model)
        except KeyboardInterrupt:
            print("\nVoice mode stopped.")
            break

        if not user_text:
            speak("I didn't catch that.")
            continue

        if user_text.lower() in EXIT_PHRASES:
            speak("Goodbye.")
            break

        try:
            reply, chat_history = handle_fn(user_text, chat_history)
        except Exception as e:
            reply = f"Error: {e}"

        print("\nJarvis >", reply)
        speak(reply)
        time.sleep(0.1)
