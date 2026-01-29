"""Local/Cloud TTS provider using Microsoft Edge TTS (free, no API key needed)."""
import asyncio
import io
from typing import Optional
import edge_tts
from .base import TTSProvider


class EdgeTTS(TTSProvider):
    """TTS using Microsoft Edge TTS (free, requires internet)."""
    
    # Popular voices - full list at: edge-tts --list-voices
    VOICES = {
        "en-US-female": "en-US-AriaNeural",
        "en-US-male": "en-US-GuyNeural",
        "en-GB-female": "en-GB-SoniaNeural",
        "en-GB-male": "en-GB-RyanNeural",
        "es-ES-female": "es-ES-ElviraNeural",
        "es-ES-male": "es-ES-AlvaroNeural",
        "fr-FR-female": "fr-FR-DeniseNeural",
        "fr-FR-male": "fr-FR-HenriNeural",
        "de-DE-female": "de-DE-KatjaNeural",
        "de-DE-male": "de-DE-ConradNeural",
        "it-IT-female": "it-IT-ElsaNeural",
        "it-IT-male": "it-IT-DiegoNeural",
        "pt-BR-female": "pt-BR-FranciscaNeural",
        "pt-BR-male": "pt-BR-AntonioNeural",
        "ja-JP-female": "ja-JP-NanamiNeural",
        "ja-JP-male": "ja-JP-KeitaNeural",
        "zh-CN-female": "zh-CN-XiaoxiaoNeural",
        "zh-CN-male": "zh-CN-YunxiNeural",
        "ko-KR-female": "ko-KR-SunHiNeural",
        "ko-KR-male": "ko-KR-InJoonNeural",
    }
    
    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
        rate: str = "+0%",  # -50% to +100%
        volume: str = "+0%",  # -50% to +100%
        pitch: str = "+0Hz",  # -50Hz to +50Hz
    ):
        """
        Initialize Edge TTS.
        
        Args:
            voice: Voice name (see VOICES dict or use edge-tts --list-voices)
            rate: Speech rate adjustment
            volume: Volume adjustment
            pitch: Pitch adjustment
            
        Examples:
            voice="en-US-AriaNeural"  # US English female
            voice="es-ES-ElviraNeural"  # Spanish female
            rate="+20%"  # 20% faster
            volume="-10%"  # 10% quieter
        """
        # If shorthand is used, convert to full voice name
        if voice in self.VOICES:
            voice = self.VOICES[voice]
        
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.sample_rate = 24000  # Edge TTS output is 24kHz
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to MP3 audio bytes."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch
        )
        
        # Collect all audio chunks
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": "mp3",
            "sample_rate": self.sample_rate,
            "channels": 1,
            "codec": "mp3",
        }
    
    @staticmethod
    async def list_voices():
        """List all available voices."""
        voices = await edge_tts.list_voices()
        return voices