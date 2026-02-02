# src/llm/llm_provider.py
from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Optional

class LLMProvider(ABC):    
    """Base class for Language Model providers."""
    
    def __init__(
        self,
        max_history: int = 1000,
        knowledge_base: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize LLM provider.
        
        Args:
            max_history: Maximum number of conversation turns to keep
            knowledge_base: Optional dict of {question: answer} for RAG
        """
        self.max_history = max_history
        self.knowledge_base = knowledge_base or {}
        self.system_prompt = self._default_system_prompt()
        self.conversation_history: List[Dict[str, str]] = []
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for voice assistant."""
        return (
            "RESPONSE LANGUAGE: The response needs to be strictly in English, even if the input language is hindi\n"
            "ROLE: Female Voice assistant for Subharti University help desk.\n"
            "DOMAIN: University operations, admissions, exams, attendance, facilities, general queries.\n"
            "STYLE: Concise, factual, voice-friendly. Speak naturally like a human assistant. Do not give seperate paragraphs, just one big paragraph. "
            "Avoid using bullet points, numbered lists, headings,symbols like asterisks, etc or any formatted text. "
            "Respond in complete sentences that flow naturally in spoken conversation. "
            "Do not return abbreviations, convert to full words like Prof. to Professor or "
            "if names have abbreviations like Dr. Pramod K. Sharma only return Doctor Promod Sharma. "
            "Refer the university as The university and not by its name when possible.\n"
            "TONE: Friendly, helpful, and patient. Use natural transitions like 'Let me tell you about that,' "
            "'For example,' or 'Also, I should mention.'\n"
            "UNKNOWN: Politely say if information is not available. "
            "Example: 'I m sorry, I don't have that specific information right now.'\n\n"
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
    
    def _build_messages(self, text: str, use_history: bool = True) -> List[Dict[str, str]]:
        """
        Build message list with system prompt, history, and current message.
        
        Args:
            text: Current user input
            use_history: Whether to include conversation history
            
        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if use_history and len(self.conversation_history) > 1:
            messages.extend(self.conversation_history[:-1])
        
        messages.append({"role": "user", "content": text})
        
        return messages
    
    @abstractmethod
    async def generate_stream(self, text: str, use_history: bool = True) -> AsyncIterator[str]:
        """
        Generate streaming response from text input.
        
        Args:
            text: Input text to generate response for
            use_history: Whether to include conversation history
            
        Yields:
            Text chunks as they're generated
        """
        pass