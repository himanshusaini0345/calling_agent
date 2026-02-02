"""Local TTS provider using Piper."""
import asyncio
import wave
import io
from typing import Optional
import subprocess
import tempfile
import os

from src.tts.tts_provider import TTSProvider


class PiperTTS(TTSProvider):
    """Local TTS using Piper (CPU-based)."""
    
    def __init__(
        self,
        model_path: str,
        config_path: Optional[str] = None,
        speaker_id: Optional[int] = None,
    ):
        """
        Initialize Piper TTS.
        
        Args:
            model_path: Path to .onnx model file
            config_path: Path to .json config file (optional, auto-derived from model_path)
            speaker_id: Speaker ID for multi-speaker models
        """
        print(f"Loading Piper voice model: {model_path}")
        
        self.model_path = model_path
        self.sample_rate = 22050  # or read once from json if you want

    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to WAV audio bytes."""
        # Run synthesis in thread pool to avoid blocking
        wav_bytes = await asyncio.to_thread(self._synthesize_sync, text)
        return wav_bytes
    
    def _synthesize_sync(self, text: str) -> bytes:
        if not text.strip():
            return b""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_wav = f.name

        try:
            proc = subprocess.run(
                [
                    "piper",
                    "--model", self.model_path,
                    "--output_file", temp_wav,
                ],
                input=text.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            with open(temp_wav, "rb") as f:
                wav_bytes = f.read()

            # 🔥 HARD GUARANTEE (keep this)
            if len(wav_bytes) <= 44:
                raise RuntimeError("Piper produced header-only WAV")

            return wav_bytes

        finally:
            if os.path.exists(temp_wav):
                os.unlink(temp_wav)

    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }
