from abc import ABC, abstractmethod
from typing import AsyncIterator

class STTProvider(ABC):
    """Base class for Speech-to-Text providers."""
    
    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
        """
        Transcribe streaming audio to text.
        
        Args:
            audio_stream: AsyncIterator yielding audio chunks
            
        Yields:
            Final transcribed text when available
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass

