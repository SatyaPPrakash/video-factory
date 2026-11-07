import asyncio, os, subprocess
import edge_tts
from gtts import gTTS

VOICE = "en-US-AndrewMultilingualNeural"

def _ok(path):
    return os.path.exists(path) and os.path.getsize(path) > 1000

def speak(text, path):
    path = str(path)
    try:
        asyncio.run(edge_tts.Communicate(text, VOICE).save(path))
        if not _ok(path):
            raise RuntimeError("empty audio")
    except Exception:
        try:
            gTTS(text, lang="en").save(path)
        except Exception:
            secs = max(3, len(text.split()) / 2.5)
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                            "-t", str(secs), "-c:a", "libmp3lame", path],
                           check=True, capture_output=True)
