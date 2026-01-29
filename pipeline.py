"""Voice assistant pipeline orchestrating STT -> LLM -> TTS."""
import asyncio
from time import perf_counter
from typing import AsyncIterator, Callable, Optional
from providers.base import STTProvider, LLMProvider, TTSProvider


class VoicePipeline:
    """Pipeline orchestrating STT, LLM, and TTS providers."""
    
    def __init__(
        self,
        stt: STTProvider,
        llm: LLMProvider,
        tts: TTSProvider,
        sentence_delimiters: tuple = (".", "!", "?", ","),
        enable_timing: bool = True,
    ):
        """
        Initialize voice pipeline.
        
        Args:
            stt: Speech-to-text provider
            llm: Language model provider
            tts: Text-to-speech provider
            sentence_delimiters: Punctuation marks that trigger TTS
            enable_timing: Enable performance timing logs
        """
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.sentence_delimiters = sentence_delimiters
        self.enable_timing = enable_timing
    
    async def process_utterance(
        self,
        text: str,
        audio_callback: Callable[[bytes, int], asyncio.Task],
    ):
        """
        Process a single user utterance through LLM and TTS.
        
        Args:
            text: Transcribed user input
            audio_callback: Async callback function(audio_bytes, sequence_number)
        """
        t0 = perf_counter()
        
        if self.enable_timing:
            print(f"\n👤 USER: {text}")
            print(f"⏱️  STT complete @ 0 ms")
        
        buffer = ""
        seq = 0
        first_token = True
        first_audio = True
        
        # Stream LLM response
        async for chunk in self.llm.generate_stream(text):
            if first_token and self.enable_timing:
                print(f"⏱️  LLM first token @ {(perf_counter()-t0)*1000:.0f} ms")
                first_token = False
            
            buffer += chunk
            
            # Check if we hit a sentence delimiter
            if any(buffer.endswith(delim) for delim in self.sentence_delimiters):
                sentence = buffer.strip()
                buffer = ""
                
                if not sentence:
                    continue
                
                if self.enable_timing:
                    print(f"🗣️  TTS chunk: {sentence}")
                
                # Synthesize audio
                t_tts_start = perf_counter()
                audio = await self.tts.synthesize(sentence)
                
                if self.enable_timing:
                    t_audio = (perf_counter() - t0) * 1000
                    print(f"⏱️  TTS done @ {t_audio:.0f} ms ({len(audio)} bytes)")
                
                # Send audio via callback
                await audio_callback(audio, seq)
                
                if first_audio and self.enable_timing:
                    t_first = (perf_counter() - t0) * 1000
                    print(f"⏱️  First audio sent @ {t_first:.0f} ms")
                    first_audio = False
                
                seq += 1
        
        # Flush remaining buffer
        if buffer.strip():
            audio = await self.tts.synthesize(buffer.strip())
            await audio_callback(audio, seq)
        
        if self.enable_timing:
            total = (perf_counter() - t0) * 1000
            print(f"⏱️  Total time: {total:.0f} ms\n")
    
    async def run(
        self,
        audio_input_stream: AsyncIterator[bytes],
        audio_callback: Callable[[bytes, int], asyncio.Task],
    ):
        """
        Run the complete pipeline.
        
        Args:
            audio_input_stream: Stream of incoming audio chunks
            audio_callback: Callback for sending generated audio
        """
        # Stream transcription
        async for text in self.stt.transcribe_stream(audio_input_stream):
            # Process each transcribed utterance
            await self.process_utterance(text, audio_callback)
    
    async def cleanup(self):
        """Clean up all providers."""
        await self.stt.close()
