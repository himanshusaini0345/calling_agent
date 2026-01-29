"""Local TTS provider using Coqui TTS."""
import asyncio
import io
import numpy as np
from typing import Optional
from TTS.api import TTS
from .base import TTSProvider


class CoquiTTS(TTSProvider):
    """Local TTS using Coqui TTS (CPU-based, replaces Piper)."""
    
    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        use_gpu: bool = False,
        speaker_id: Optional[str] = None,
        language: Optional[str] = None,
    ):
        """
        Initialize Coqui TTS.
        
        Args:
            model_name: Model name from Coqui TTS zoo
            use_gpu: Whether to use GPU (False for CPU)
            speaker_id: Speaker ID for multi-speaker models
            language: Language code for multilingual models
            
        Popular models:
            - "tts_models/en/ljspeech/tacotron2-DDC" (English, fast)
            - "tts_models/en/ljspeech/glow-tts" (English, quality)
            - "tts_models/multilingual/multi-dataset/your_tts" (100+ languages)
            - "tts_models/en/vctk/vits" (English, multi-speaker)
        """
        print(f"Loading Coqui TTS model: {model_name}")
        self.tts = TTS(model_name=model_name, gpu=use_gpu)
        self.speaker_id = speaker_id
        self.language = language
        self.sample_rate = self.tts.synthesizer.output_sample_rate if hasattr(self.tts, 'synthesizer') else 22050
        
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to WAV audio bytes."""
        # Run synthesis in thread pool to avoid blocking
        wav_data = await asyncio.to_thread(self._synthesize_sync, text)
        return wav_data
    
    def _synthesize_sync(self, text: str) -> bytes:
        """Synchronous synthesis (run in thread pool)."""
        # Create temporary file path
        import tempfile
        import wave
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Synthesize to file
            if self.speaker_id and self.language:
                # Multilingual multi-speaker
                self.tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    speaker=self.speaker_id,
                    language=self.language
                )
            elif self.speaker_id:
                # Multi-speaker only
                self.tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    speaker=self.speaker_id
                )
            elif self.language:
                # Multilingual only
                self.tts.tts_to_file(
                    text=text,
                    file_path=tmp_path,
                    language=self.language
                )
            else:
                # Single speaker, single language
                self.tts.tts_to_file(
                    text=text,
                    file_path=tmp_path
                )
            
            # Read WAV file
            with open(tmp_path, 'rb') as f:
                wav_bytes = f.read()
            
            return wav_bytes
            
        finally:
            # Clean up temp file
            import os
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }