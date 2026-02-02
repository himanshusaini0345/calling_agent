"""Local TTS provider using Piper with streaming."""
import asyncio
import re
import wave
import io
import struct
from typing import Optional
import subprocess
from src.tts.tts_provider import TTSProvider

class PiperTTS(TTSProvider):
    """Local TTS using Piper (CPU-based) with streaming."""
    
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
        self.config_path = config_path
        self.speaker_id = speaker_id
        self.sample_rate = 22050
        self._process = None
        self._lock = asyncio.Lock()
        
    async def _ensure_process(self):
        """Ensure Piper process is running."""
        if self._process is None or self._process.returncode is not None:
            cmd = [
                "piper",
                "--model", self.model_path,
                "--output-raw",  # Output raw PCM to stdout
            ]
            
            if self.config_path:
                cmd.extend(["--config", self.config_path])
            
            if self.speaker_id is not None:
                cmd.extend(["--speaker", str(self.speaker_id)])
            
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
    def _normalize_text(self, text: str) -> str:
            """Normalize text for faster TTS."""
            # Expand abbreviations
            text = re.sub(r'\bProf\.\s*', 'Professor ', text)
            text = re.sub(r'\bDr\.\s*', 'Doctor ', text)
            text = re.sub(r'\bMrs\.\s*', 'Misses ', text)
            text = re.sub(r'\bMr\.\s*', 'Mister ', text)
            
            # Break up complex names (helps Piper chunk better)
            text = re.sub(r'([A-Z][a-z]+)\s+([A-Z]\.)\s+([A-Z][a-z]+)', 
                        r'\1, \2 \3', text)
            return text
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to WAV audio bytes."""
        if not text.strip():
            return self._create_empty_wav()
        
        # Normalize before synthesis
        normalized = self._normalize_text(text)
        
        async with self._lock:
            await self._ensure_process()
            
            # Send text to Piper
            self._process.stdin.write(normalized.encode("utf-8") + b"\n")
            await self._process.stdin.drain()
            
            # Read raw PCM output
            pcm_data = await self._read_pcm_output()
            
            if len(pcm_data) == 0:
                raise RuntimeError("Piper produced no audio data")
            
            # Convert PCM to WAV
            wav_bytes = self._pcm_to_wav(pcm_data)
            
            if len(wav_bytes) <= 44:
                raise RuntimeError("Piper produced header-only WAV")
            
            return wav_bytes
    
    async def _read_pcm_output(self) -> bytes:
        """Read PCM output from Piper process."""
        # Read until we get a size marker or timeout
        # Piper outputs raw PCM, you may need to adjust based on your version
        chunks = []
        
        # Read in chunks with timeout
        try:
            while True:
                chunk = await asyncio.wait_for(
                    self._process.stdout.read(8192),
                    timeout=5.0
                )
                if not chunk:
                    break
                chunks.append(chunk)
                
                # Check if we have enough data (simple heuristic)
                # Adjust based on typical sentence length
                if len(b"".join(chunks)) > 16384:  # ~0.37s at 22050Hz
                    # Check if more data is immediately available
                    try:
                        extra = await asyncio.wait_for(
                            self._process.stdout.read(8192),
                            timeout=0.1
                        )
                        if extra:
                            chunks.append(extra)
                        else:
                            break
                    except asyncio.TimeoutError:
                        break
        except asyncio.TimeoutError:
            pass
        
        return b"".join(chunks)
    
    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
        """Convert raw PCM to WAV format."""
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_data)
        
        return wav_buffer.getvalue()
    
    def _create_empty_wav(self) -> bytes:
        """Create empty WAV file."""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b"")
        return wav_buffer.getvalue()
    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": "wav",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "bit_depth": 16,
        }
    
    async def close(self):
        """Clean up resources."""
        if self._process:
            self._process.stdin.close()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()