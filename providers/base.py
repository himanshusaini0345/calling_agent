"""Base interfaces for STT, LLM, and TTS providers."""
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


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


class LLMProvider(ABC):
    """Base class for Language Model providers."""
    
    @abstractmethod
    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        """
        Generate streaming response from text input.
        
        Args:
            text: Input text to generate response for
            
        Yields:
            Text chunks as they're generated
        """
        pass


class TTSProvider(ABC):
    """Base class for Text-to-Speech providers."""
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes (format depends on provider)
        """
        pass
    
    @abstractmethod
    def get_audio_format(self) -> dict:
        """
        Get audio format information.
        
        Returns:
            Dict with 'format', 'sample_rate', 'channels', etc.
        """
        pass
