"""Local TTS provider using Piper."""
import asyncio
import wave
import io
from typing import Optional
from piper import PiperVoice
from .base import TTSProvider


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
        
        if config_path is None:
            config_path = model_path + ".json"
        
        self.voice = PiperVoice.load(model_path, config_path=config_path)
        self.speaker_id = speaker_id
        self.sample_rate = self.voice.config.sample_rate
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to WAV audio bytes."""
        # Run synthesis in thread pool to avoid blocking
        wav_bytes = await asyncio.to_thread(self._synthesize_sync, text)
        return wav_bytes
    
    def _synthesize_sync(self, text: str) -> bytes:
        """Synchronous synthesis (run in thread pool)."""
        # Create in-memory WAV file
        wav_io = io.BytesIO()
        
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setframerate(self.sample_rate)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setnchannels(1)  # Mono
            
            # Synthesize audio
            self.voice.synthesize(
                text,
                wav_file
            )
        
        raw = wav_io.getvalue()

        print("🔍 WAV_BYTES_LEN:", len(raw))
        print("🔍 WAV_BYTES_HEX:", raw[:64].hex(" "))

        return raw

    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }
