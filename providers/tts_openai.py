"""OpenAI Text-to-Speech provider."""
import io
import os
import tempfile
import wave
import asyncio
from openai import AsyncOpenAI, OpenAI
from .base import TTSProvider


class OpenAITTS(TTSProvider):
    """TTS provider using OpenAI voices (low latency, high quality)."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini-tts",
        voice: str = "alloy",
        sample_rate: int = 16000,
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.voice = voice
        self.sample_rate = sample_rate

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to WAV audio bytes.
        """
        # Call the async create method directly
        response = await self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=text,
            response_format="wav",  # Specify WAV format
        )
    
        audio_bytes = response.content
        
        print("🔊 WAV_BYTES:", len(audio_bytes))
        return audio_bytes

    def get_audio_format(self) -> dict:
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }
