"""OpenAI LLM provider with conversation history and knowledge base support."""
from typing import AsyncIterator, List, Dict, Optional
from openai import AsyncOpenAI
from .base import LLMProvider


class OpenAILLM(LLMProvider):
    """LLM provider using OpenAI API with conversation history and RAG support."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
        max_history: int = 1000,
        knowledge_base: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4o-mini, gpt-4o, etc.)
            system_prompt: Optional system prompt
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
        """Generate default system prompt."""
        base_prompt = ( 
            "You are a helpful female voice assistant for Subharti University help desk. "
            "You may also handle simple conversational requests (such as greetings, counting, or clarifications)"
            "to keep the interaction natural, but always gently steer the conversation back to university-related help when appropriate."
            "You assist students, faculty, and staff with their questions about university operations, "
            "attendance, leaves, admissions, events, and general queries.\n\n"
            
            "Guidelines:\n" 
            "- Keep responses concise and conversational for voice interaction\n"
            "- Be polite and professional\n"
            "- If you don't know something, say so honestly\n"
            "- Use the knowledge base information when available\n"
            "- Respond in the same language as the user (English or Hindi)\n"
        )
        
        if self.knowledge_base:
            base_prompt += (
                "\n\nKnowledge Base:\n"
                "Use the following Q&A pairs to answer questions when relevant:\n\n"
            )
            for i, (q, a) in enumerate(list(self.knowledge_base.items()), 1):
                # Truncate long answers for context window
                base_prompt += f"{i}. Q: {q}\n   A: {a}\n\n"
        
        return base_prompt
    
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
    
    def _find_relevant_context(self, query: str) -> Optional[str]:
        """Find relevant context from knowledge base using simple keyword matching."""
        query_lower = query.lower()
        
        # Simple keyword matching
        best_match = None
        best_score = 0
        
        for question, answer in self.knowledge_base.items():
            
            # Count matching words
            question_words = set(question.lower().split())
            query_words = set(query_lower.split())
            matching_words = question_words.intersection(query_words)
            score = len(matching_words)
            
            if score > best_score:
                best_score = score
                best_match = answer
        
        # Return match if score is significant
        if best_score >= 2:  # At least 2 matching words
            return best_match
        
        return None
    
    async def generate_stream(self, text: str, use_history: bool = True) -> AsyncIterator[str]:
        """
        Generate streaming response using OpenAI Chat Completions API.
        
        Args:
            text: User input
            use_history: Whether to include conversation history
            
        Yields:
            Text chunks as they're generated
        """
        # Find relevant context from knowledge base
        relevant_context = self._find_relevant_context(text)
        
        # Build user message with context if found
        user_message = text
        # if relevant_context:
        #     user_message = (
        #         f"User query: {text}\n\n"
        #         f"Relevant information from knowledge base:\n{relevant_context}\n\n"
        #         "Please use this information to answer the user's question naturally."
        #     )
        
        # Add user message to history (original text, not augmented)
        self.add_to_history("user", text)
        
        # Build messages array
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if use_history and len(self.conversation_history) > 1:
            # Add conversation history (excluding the just-added user message)
            messages.extend(self.conversation_history[:-1])
        
        # Add current user message (with context if found)
        messages.append({"role": "user", "content": user_message})
        
        # _debug_print_messages(messages)
        
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
