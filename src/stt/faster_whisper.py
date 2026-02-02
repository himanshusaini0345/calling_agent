"""Local STT provider using Faster Whisper."""
import asyncio
from time import monotonic
import numpy as np
from typing import AsyncIterator
from faster_whisper import WhisperModel

from src.stt.stt_provider import STTProvider


class FasterWhisperSTT(STTProvider):
    """Local multilingual STT using Faster Whisper (CPU-based)."""
    
    def __init__(
        self,
        model: WhisperModel,
        language: str = "en",
        vad_filter: bool = True,
        min_audio_seconds: float = 1.0,
    ):
        """
        Initialize Faster Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            language: Language code (None for auto-detection)
            device: "cpu" or "cuda"
            compute_type: "int8", "int16", "float16", "float32"
            vad_filter: Enable voice activity detection
        """
        self.model = model
        self.language = language
        self.vad_filter = vad_filter
        self.sample_rate = 16000
        self.buffer = bytearray()
        self.min_chunk_size = self.sample_rate * 2 * min_audio_seconds # 1 second of 16-bit audio
        self.text_buffer: list[str] = []

    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
        """Transcribe streaming audio chunks."""
        async for chunk in audio_stream:
            self.buffer.extend(chunk)
            
            # Process when we have enough data
            if len(self.buffer) < self.min_chunk_size:
                continue

            audio_data = bytes(self.buffer)
            self.buffer.clear()
            
            # Convert bytes to numpy array (16-bit PCM)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Run transcription in thread pool to avoid blocking
            segments, _ = await asyncio.to_thread(
                self._transcribe,
                audio_np
            )
            

            utterance = " ".join(
                segment.text.strip()
                for segment in segments
                if segment.text.strip()
            )

            if utterance:
                yield utterance                  
    
    def _transcribe(self, audio_np):
        """Synchronous transcription (run in thread pool)."""
        segments, info = self.model.transcribe(
            audio_np,
            language=self.language,
            vad_filter=self.vad_filter,
            without_timestamps=True,    
        )
        # Convert generator to list to ensure all segments are processed
        return list(segments), info
    
    async def close(self):
        """Clean up resources."""
        # Faster Whisper doesn't need explicit cleanup
        pass
