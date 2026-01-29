import asyncio
import io
import os
import tempfile
import wave
import pyttsx3
from .base import TTSProvider


class EspeakTTS(TTSProvider):
    """
    Local fast TTS using espeak-ng (via pyttsx3).
    Optimized for fake streaming.
    """

    def __init__(self, rate: int = 170, voice_hint: str = "english"):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)

        # Pick English voice explicitly
        for v in self.engine.getProperty("voices"):
            if voice_hint.lower() in v.name.lower():
                self.engine.setProperty("voice", v.id)
                break

        self.sample_rate = 22050  # pyttsx3 default

    async def synthesize(self, text: str) -> bytes:
        print("🧪 TTS_ENTER:", repr(text))
        audio = await asyncio.to_thread(self._synthesize_sync, text)
        print("🧪 TTS_EXIT bytes=", len(audio))
        return audio

    def _synthesize_sync(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as f:
            path = f.name
            
        try:
            with open(path, "rb") as f:
                data = f.read()

            print("🔊 WAV_BYTES:", len(data))

            return data
        finally:
            os.remove(path)

    def get_audio_format(self) -> dict:
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }
