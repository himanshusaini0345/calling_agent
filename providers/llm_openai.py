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
        self.system_prompt = system_prompt or (
            "You are a real-time conversational voice assistant. "
            "Speak naturally, casually, and clearly, as if talking to a person. "

            "Match the language of the user's input. "
            "If the user speaks English, respond in English. "
            "If the user switches language, switch with them. "

            "Use light backchanneling where it feels natural, such as "
            "'uh-huh', 'mm-hmm', 'I see', 'right', or 'okay', "
            "but do not overuse them and never at the start of every sentence. "

            "Respond in flowing spoken sentences. "
            "Do NOT use numbered lists, bullet points, headings, or structured formatting. "
            "Avoid phrases like 'first', 'second', 'here are', or reading-style explanations. "

            "Keep sentences short and easy to listen to. "
            "The response should sound natural when spoken aloud."
        )

    
    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI's Responses API."""
        async with self.client.responses.stream(
            model=self.model,
            input=text,
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
