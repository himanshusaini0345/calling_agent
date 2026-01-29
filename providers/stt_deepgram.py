"""Deepgram STT provider."""
import asyncio
import json
import websockets
from typing import AsyncIterator
from .base import STTProvider


class DeepgramSTT(STTProvider):
    """Cloud-based STT using Deepgram."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "nova-2",
        language: str = "en",
        sample_rate: int = 16000,
    ):
        """
        Initialize Deepgram STT.
        
        Args:
            api_key: Deepgram API key
            model: Model name (nova-2, nova, base, enhanced)
            language: Language code (en, es, fr, etc.)
            sample_rate: Audio sample rate in Hz
        """
        self.api_key = api_key
        self.model = model
        self.language = language
        self.sample_rate = sample_rate
        self.ws = None
        
        self.ws_url = (
            f"wss://api.deepgram.com/v1/listen"
            f"?model={model}"
            f"&language={language}"
            f"&encoding=linear16"
            f"&sample_rate={sample_rate}"
            f"&punctuate=true"
            f"&interim_results=true"
            f"&endpointing=300"
        )
    
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
        """Transcribe streaming audio via Deepgram WebSocket."""
        async with websockets.connect(
            self.ws_url,
            additional_headers={"Authorization": f"Token {self.api_key}"},
        ) as ws:
            self.ws = ws
            
            # Task to send audio
            async def send_audio():
                async for chunk in audio_stream:
                    await ws.send(chunk)
            
            send_task = asyncio.create_task(send_audio())
            
            try:
                # Receive transcriptions
                async for msg in ws:
                    data = json.loads(msg)
                    
                    if data.get("type") != "Results":
                        continue
                    
                    alt = data["channel"]["alternatives"][0]
                    text = alt.get("transcript", "").strip()
                    
                    # Only yield final results
                    if data.get("is_final") and text:
                        yield text
            finally:
                send_task.cancel()
                self.ws = None
    
    async def close(self):
        """Close WebSocket connection."""
        if self.ws:
            await self.ws.close()
