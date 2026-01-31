"""Cartesia TTS provider."""
import aiohttp

from tts.tts_provider import TTSProvider


class CartesiaTTS(TTSProvider):
    """Cloud-based TTS using Cartesia."""
    
    def __init__(
        self,
        api_key: str,
        voice_id: str = "a0e99841-438c-4a64-b679-ae501e7d6091",
        model_id: str = "sonic-english",
        output_format: str = "mp3",
        sample_rate: int = 44100,
    ):
        """
        Initialize Cartesia TTS.
        
        Args:
            api_key: Cartesia API key
            voice_id: Voice ID to use (faf0731e-dfb9-4cfc-8119-259a79b27e12)
            model_id: Model ID (sonic-3, sonic-english, sonic-multilingual)
            output_format: Audio format (mp3, wav, pcm)
            sample_rate: Sample rate in Hz
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = output_format
        self.sample_rate = sample_rate
    
    async def synthesize(self, text: str) -> bytes:
        """Synthesize text to audio bytes."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Cartesia-Version": "2025-04-16",
                    "Content-Type": "application/json",
                },
                json={
                    "model_id": self.model_id,
                    "voice": {"id": self.voice_id},
                    "transcript": text,
                    "output_format": {
                        "container": self.output_format,
                        "encoding": self.output_format,
                        "sample_rate": self.sample_rate,
                    },
                },
            ) as response:
                return await response.read()
    
    def get_audio_format(self) -> dict:
        """Get audio format information."""
        return {
            "format": self.output_format,
            "sample_rate": self.sample_rate,
            "channels": 1,
        }
