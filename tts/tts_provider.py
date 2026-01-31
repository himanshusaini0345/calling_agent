from abc import ABC, abstractmethod


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
