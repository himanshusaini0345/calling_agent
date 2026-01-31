
from abc import ABC, abstractmethod
from typing import AsyncIterator

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