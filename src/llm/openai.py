"""OpenAI LLM provider with conversation history and knowledge base support."""
from typing import AsyncIterator, List, Dict, Optional
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
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_history = max_history
        self.knowledge_base = knowledge_base or {}
        self.system_prompt = self._default_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []
    
    def _default_system_prompt(self) -> str:
        return (
            # "LANGUAGE: Hindi written in english. e.g. 'Aap kaise hain'\n"
            "RESPONSE LANGUAGE: The response nneds to be strictly in English, even if the input language is hindi\n"
            "ROLE: Female Voice assistant for Subharti University help desk.\n"
            "DOMAIN: University operations, admissions, exams, attendance, facilities, general queries.\n"
            "STYLE: Concise, factual, voice-friendly.Speak naturally like a human assistant. Avoid using bullet points, numbered lists, headings, or any formatted text. Respond in complete sentences that flow naturally in spoken conversation.\n"
            "TONE: Friendly, helpful, and patient. Use natural transitions like 'Let me tell you about that,' 'For example,' or 'Also, I should mention.'"
            "UNKNOWN: Politely say if information is not available. Example: 'I m sorry, I don't have that specific information right now.'\n\n"
            "REFERENCE CONTEXT:\n"
            f"{self.knowledge_base}"
        )

    def add_to_history(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        return self.conversation_history.copy()
    
   
    async def generate_stream(self, text: str, use_history: bool = True) -> AsyncIterator[str]:
        """
        Generate streaming response
        
        Args:
            text: User input
            use_history: Whether to include conversation history
            
        Yields:
            Text chunks as they're generated
        """
        
        user_message = text
        
        self.add_to_history("user", text)
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if use_history and len(self.conversation_history) > 1:
            messages.extend(self.conversation_history[:-1])
        
        messages.append({"role": "user", "content": user_message})
        
        # _debug_print_messages(messages)
        
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
        
        self.add_to_history("assistant", full_response)
        
def _debug_print_messages( messages: List[Dict[str, str]]):
    print("\n" + "=" * 80)
    print("📤 OPENAI REQUEST PAYLOAD")
    print("=" * 80)

    for i, msg in enumerate(messages, 1):
        role = msg["role"].upper()
        content = msg["content"]

        print(f"\n[{i}] ROLE: {role}")
        print("-" * 80)
        print(content)

    print("\n" + "=" * 80 + "\n")
