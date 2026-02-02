from typing import AsyncIterator
import asyncio
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextIteratorStreamer
import threading

from llm.llm_provider import LLMProvider

class LocalLLM(LLMProvider):
    """Lightweight local LLM with Hindi support."""
    
    def __init__(
        self, 
        model_name: str = "google/gemma-2-2b-it",
        device: str = "auto",
        max_new_tokens: int = 512
    ):
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
    
    async def generate_stream(self, text: str) -> AsyncIterator[str]:
        """Generate streaming response."""
        # Format prompt for instruction models
        messages = [{"role": "user", "content": text}]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, 
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
        for text_chunk in streamer:
            yield text_chunk
            await asyncio.sleep(0)  # Allow event loop to process
        
        thread.join()

# Usage
async def main():
    # Choose model based on your RAM:
    # - "google/gemma-2-2b-it" (4GB RAM) - Best Hindi
    # - "Qwen/Qwen2.5-1.5B-Instruct" (3GB RAM) - Fastest
    # - "meta-llama/Llama-3.2-3B-Instruct" (6GB RAM) - Best quality
    
    llm = LocalLLM(model_name="google/gemma-2-2b-it")
    
    # Test with Hindi
    async for chunk in llm.generate_stream("फीस के बारे में बताओ"):
        print(chunk, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())