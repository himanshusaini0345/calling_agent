"""OpenAI LLM provider."""
from typing import AsyncIterator
from openai import AsyncOpenAI
from .base import LLMProvider


class OpenAILLM(LLMProvider):
    """LLM provider using OpenAI API."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        system_prompt: str = None,
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4o, etc.)
            system_prompt: Optional system prompt
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful voice assistant. Keep responses concise and conversational."
    
    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI's Responses API."""
        async with self.client.responses.stream(
            model=self.model,
            input=text,
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
