"""Voice assistant pipeline orchestrating STT -> LLM -> TTS with interruption handling."""
import asyncio
import logging
from time import perf_counter
from typing import AsyncIterator, Callable, Optional
from providers.base import STTProvider, LLMProvider, TTSProvider

logger = logging.getLogger("app")

class VoicePipeline:
    """Pipeline orchestrating STT, LLM, and TTS providers with server-side audio queue management."""
    
    def __init__(
        self,
        stt: STTProvider,
        llm: LLMProvider,
        tts: TTSProvider,
        min_tts_chars,
        max_tts_chars,
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
        self.min_tts_chars = min_tts_chars
        self.max_tts_chars = max_tts_chars
        self.enable_timing = enable_timing
        self._utterance_id = 0
        self._current_task = None
    
    async def process_utterance(
        self,
        text: str,
        audio_callback: Callable[[str, dict], asyncio.Task],
        utterance_id: int
    ):
        """
        Process a single user utterance through LLM and TTS.
        
        Args:
            text: Transcribed user input
            audio_callback: Async callback function(message_type, data)
            utterance_id: ID of this utterance for interruption handling
        """
        if utterance_id != self._utterance_id:
            return  # interrupted before we started
        
        t0 = perf_counter()
        
        if self.enable_timing:
            logger.info(f"\n👤 USER: {text}")
            logger.info(f"⏱️  STT complete @ 0 ms")
        
        buffer = ""
        seq = 0
        first_token = True
        first_audio = True
        
        # Stream LLM response
        async for chunk in self.llm.generate_stream(text):
            if utterance_id != self._utterance_id:
                if self.enable_timing:
                    logger.info("⛔ Interrupted during LLM")
                return
            
            if first_token and self.enable_timing:
                logger.info(f"⏱️  LLM first token @ {(perf_counter()-t0)*1000:.0f} ms")
                first_token = False
            
            buffer += chunk
            
            hit_delimiter = any(buffer.endswith(delim) for delim in self.sentence_delimiters)
            buffer_len = len(buffer.strip())
            
            # 🚦 Decide whether to flush to TTS
            should_flush = (
                hit_delimiter and buffer_len >= self.min_tts_chars
            ) or (
                buffer_len >= self.max_tts_chars
            )

            # Check if we hit a sentence delimiter
            if should_flush:
                sentence = buffer.strip()
                buffer = ""
                
                if not sentence:
                    continue
                
                if self.enable_timing:
                    logger.info(f"🗣️  TTS chunk: {sentence}")

                # Synthesize audio
                audio = await self.tts.synthesize(sentence)
                
                # Check again if interrupted after synthesis
                if utterance_id != self._utterance_id:
                    if self.enable_timing:
                        logger.info("⛔ Interrupted during TTS")
                    return
                
                if self.enable_timing:
                    t_audio = (perf_counter() - t0) * 1000
                    logger.info(f"⏱️  TTS done @ {t_audio:.0f} ms ({len(audio)} bytes)")
                
                # Send audio chunk via callback
                await audio_callback("audio_chunk", {
                    "seq": seq,
                    "data": audio,
                    "utterance_id": utterance_id
                })
                
                if first_audio and self.enable_timing:
                    t_first = (perf_counter() - t0) * 1000
                    logger.info(f"⏱️  First audio sent @ {t_first:.0f} ms")
                    first_audio = False
                
                seq += 1
        
        # Flush remaining buffer
        if buffer.strip() and utterance_id == self._utterance_id:
            audio = await self.tts.synthesize(buffer.strip())
            if utterance_id == self._utterance_id:
                await audio_callback("audio_chunk", {
                    "seq": seq,
                    "data": audio,
                    "utterance_id": utterance_id
                })
        
        # Send completion signal
        if utterance_id == self._utterance_id:
            await audio_callback("audio_complete", {
                "utterance_id": utterance_id
            })
        
        if self.enable_timing:
            total = (perf_counter() - t0) * 1000
            logger.info(f"⏱️  Total time: {total:.0f} ms\n")
    
    async def run(
        self,
        audio_input_stream: AsyncIterator[bytes],
        audio_callback: Callable[[str, dict], asyncio.Task],
    ):
        """
        Run the complete pipeline.
        
        Args:
            audio_input_stream: Stream of incoming audio chunks
            audio_callback: Callback for sending control messages and audio
        """
        # Stream transcription
        async for text in self.stt.transcribe_stream(audio_input_stream):
            # Interrupt any ongoing response
            old_id = self._utterance_id
            self._utterance_id += 1
            current_id = self._utterance_id
            
            if self.enable_timing:
                logger.info(f"🔔 New utterance detected (ID: {current_id}, interrupting: {old_id})")
            
            # Signal client to clear audio queue
            await audio_callback("clear_queue", {
                "old_utterance_id": old_id,
                "new_utterance_id": current_id
            })
            
            # Process each transcribed utterance
            asyncio.create_task(
                self.process_utterance(text, audio_callback, current_id)
            )
    
    async def cleanup(self):
        """Clean up all providers."""
        await self.stt.close()