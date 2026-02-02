# src/llm/local_llm.py
from typing import AsyncIterator, Dict, Optional
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextIteratorStreamer
import threading

from src.llm.llm_provider import LLMProvider


class LocalLLM(LLMProvider):
    """Lightweight local LLM with Hindi support."""
    
    def __init__(
        self, 
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",# "google/gemma-2-2b-it" or "Qwen/Qwen2.5-1.5B-Instruct" or "Qwen/Qwen2.5-0.5B-Instruct"
        device: str = "auto",
        max_new_tokens: int = 512,
        max_history: int = 1000,
        knowledge_base: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize Local LLM.
        
        Args:
            model_name: HuggingFace model name
            device: Device to load model on ("auto", "cpu", "cuda")
            max_new_tokens: Maximum tokens to generate
            max_history: Maximum number of conversation turns to keep
            knowledge_base: Optional dict of {question: answer} for RAG
        """
        super().__init__(max_history=max_history, knowledge_base=knowledge_base)
        
        print(f"Loading model: {model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map=device,
            low_cpu_mem_usage=True
        )
        self.max_new_tokens = max_new_tokens
        
        print(f"✅ Model loaded on {self.model.device}")
    
    def _format_messages_for_local_model(
        self, 
        messages: list[Dict[str, str]]
    ) -> list[Dict[str, str]]:
        """
        Convert messages with system role to user/assistant format.
        
        Gemma and many local models don't support 'system' role.
        We merge system prompt into first user message.
        
        Args:
            messages: List of messages with potential 'system' role
            
        Returns:
            Messages formatted for models without system role support
        """
        formatted = []
        system_content = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                formatted.append(msg)
        
        # Prepend system prompt to first user message
        if system_content and formatted and formatted[0]["role"] == "user":
            formatted[0] = {
                "role": "user",
                "content": f"{system_content}\n\nUser: {formatted[0]['content']}"
            }
        
        return formatted
    
    def _merge_consecutive_user_messages(
        self, 
        messages: list[Dict[str, str]]
    ) -> list[Dict[str, str]]:
        """
        Merge consecutive user messages into one.
        
        This handles interruptions where multiple user messages appear without
        assistant responses in between.
        
        Args:
            messages: List of messages
            
        Returns:
            Messages with consecutive user messages merged
        """
        if not messages:
            return messages
        
        merged = []
        i = 0
        
        while i < len(messages):
            current = messages[i]
            
            if current["role"] == "user":
                # Collect all consecutive user messages
                user_contents = [current["content"]]
                j = i + 1
                
                while j < len(messages) and messages[j]["role"] == "user":
                    user_contents.append(messages[j]["content"])
                    j += 1
                
                # Merge them into one user message
                merged_content = "\n\n".join(user_contents)
                merged.append({"role": "user", "content": merged_content})
                
                i = j
            else:
                merged.append(current)
                i += 1
        
        return merged
    
    async def generate_stream(self, text: str, use_history: bool = True) -> AsyncIterator[str]:
        """
        Generate streaming response.
        
        Args:
            text: User input
            use_history: Whether to include conversation history
            
        Yields:
            Text chunks as they're generated
        """
        # Check if last message in history is also from user (interrupted case)
        if self.conversation_history and self.conversation_history[-1]["role"] == "user":
            # Merge the interrupted message with new message
            old_content = self.conversation_history[-1]["content"]
            self.conversation_history[-1] = {
                "role": "user",
                "content": f"{old_content}\n\n{text}"
            }
        else:
            # Normal case: add new user message
            self.add_to_history("user", text)
        
        # Build messages with system prompt and history
        messages = self._build_messages(text, use_history)
        
        # Ensure messages alternate properly (defensive check)
        messages = self._merge_consecutive_user_messages(messages)
        
        # Convert system role to user role (Gemma doesn't support system)
        formatted_messages = self._format_messages_for_local_model(messages)
        
        # Format prompt for instruction models
        formatted_prompt = self.tokenizer.apply_chat_template(
            formatted_messages, 
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(
            formatted_prompt, 
            return_tensors="pt"
        ).to(self.model.device)
        
        # Setup streaming
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        generation_kwargs = {
            **inputs,
            "streamer": streamer,
            "max_new_tokens": self.max_new_tokens,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "repetition_penalty": 1.1
        }
        
        # Run generation in thread to avoid blocking
        thread = threading.Thread(
            target=self.model.generate,
            kwargs=generation_kwargs
        )
        thread.start()
        
        # Stream tokens asynchronously
        full_response = ""
        try:
            for text_chunk in streamer:
                full_response += text_chunk
                yield text_chunk
                await asyncio.sleep(0)  # Allow event loop to process
        except Exception as e:
            print(f"❌ Generation error: {e}")
            raise
        finally:
            thread.join()
        
        # Add assistant response to history
        self.add_to_history("assistant", full_response)


# Usage example
async def main():
    # Test with knowledge base
    knowledge = {
        "fees": "Fees vary by program. Contact admissions for details.",
        "chancellor": "The Chancellor is Mrs. Stuti Narain Kacker."
    }
    
    llm = LocalLLM(
        model_name="google/gemma-2-2b-it",
        knowledge_base=knowledge
    )
    
    # Test with Hindi
    print("User: फीस के बारे में बताओ")
    print("Assistant: ", end="", flush=True)
    async for chunk in llm.generate_stream("फीस के बारे में बताओ"):
        print(chunk, end="", flush=True)
    print("\n")
    
    # Test conversation history
    print("User: और चांसलर का नाम?")
    print("Assistant: ", end="", flush=True)
    async for chunk in llm.generate_stream("और चांसलर का नाम?"):
        print(chunk, end="", flush=True)
    print("\n")
    
    # Simulate interruption - two user messages in a row
    print("\n--- Simulating interruption ---")
    llm.add_to_history("user", "फाइंस ऑफिसर")  # Interrupted, no response
    
    print("User: का नाम क्या है?")
    print("Assistant: ", end="", flush=True)
    async for chunk in llm.generate_stream("का नाम क्या है?"):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())