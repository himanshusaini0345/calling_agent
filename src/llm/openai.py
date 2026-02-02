# src/llm/openai_llm.py
from typing import AsyncIterator, Dict, Optional
from openai import AsyncOpenAI

from src.llm.llm_provider import LLMProvider


class OpenAILLM(LLMProvider):
    """LLM provider using OpenAI API with conversation history and RAG support."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_history: int = 1000,
        knowledge_base: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4o, etc.)
            max_history: Maximum number of conversation turns to keep
            knowledge_base: Optional dict of {question: answer} for RAG
        """
        super().__init__(max_history=max_history, knowledge_base=knowledge_base)
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_stream(self, text: str, use_history: bool = True) -> AsyncIterator[str]:
        """
        Generate streaming response.
        
        Args:
            text: User input
            use_history: Whether to include conversation history
            
        Yields:
            Text chunks as they're generated
        """
        # Add user message to history
        self.add_to_history("user", text)
        
        # Build messages with system prompt and history
        messages = self._build_messages(text, use_history)
        
        # Stream response
        full_response = ""
        async with self.client.responses.stream(
            model=self.model,
            input=messages,
            temperature=0.7,
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    full_response += event.delta
                    yield event.delta
        
        # Add assistant response to history
        self.add_to_history("assistant", full_response)