import logging
from typing import AsyncIterator
import torch
import torchaudio
import numpy as np
import asyncio
from collections import deque
from transformers import AutoModel

from transformers import AutoModel

from src.stt.stt_provider import STTProvider
logger = logging.getLogger("app")

class IndicConformerSTT(STTProvider):
    """
    Streaming STT using HuggingFace Indic-Conformer.
    Endpointing via RMS-based silence detection.
    """

    def __init__(   
        self,
        model: AutoModel,
        language: str = "hi",
        decoder_type: str = "ctc",   # "ctc" or "rnnt"
        input_sample_rate: int = 16000,
        target_sample_rate: int = 16000,
        silence_threshold: float = 0.02,
        silence_duration: float = 0.25   ,
        min_speech_duration: float = 0.3,
        chunk_duration: float = 0.256,
    ):
        if model is None:
            raise ValueError("IndicConformerSTT received None model")
        self.language = language
        self.decoder_type = decoder_type
        self.input_sample_rate = input_sample_rate
        self.target_sample_rate = target_sample_rate

        self.silence_threshold = silence_threshold
        self.chunk_duration = chunk_duration

        self.silence_chunks_threshold = int(silence_duration / chunk_duration)
        self.min_speech_chunks = int(min_speech_duration / chunk_duration)

        self.audio_chunks = deque()
        self.silence_chunks = 0

        self.model = model

        self.resampler = None
        if input_sample_rate != target_sample_rate:
            self.resampler = torchaudio.transforms.Resample(
                orig_freq=input_sample_rate,
                new_freq=target_sample_rate
            )

    def _rms(self, x: np.ndarray) -> float:
        return np.sqrt(np.mean(x ** 2))

    def _decode_buffer(self) -> str:
        if len(self.audio_chunks) < self.min_speech_chunks:
            self.audio_chunks.clear()
            return ""

        audio = np.concatenate(self.audio_chunks)
        logger.info(f"🧠 Decoding {len(audio)} samples")

        self.audio_chunks.clear()

        wav = torch.from_numpy(audio).float()

        if self.resampler is not None:
            wav = self.resampler(wav.unsqueeze(0)).squeeze(0)

        if wav.ndim > 1:
            wav = torch.mean(wav, dim=0)

        wav = wav.unsqueeze(0)  # [1, T]

        with torch.no_grad():
            text = self.model(wav, self.language, self.decoder_type)

        return text.strip()

    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
        
        async for audio_bytes in audio_stream:
            chunk = (
                np.frombuffer(audio_bytes, dtype=np.int16)
                .astype(np.float32) / 32768.0
            )
            # rms = self._rms(chunk)
            # logger.info(f"🎚 RMS={rms:.4f}")
                
            if self._rms(chunk) < self.silence_threshold:
                self.silence_chunks += 1

                if self.silence_chunks >= self.silence_chunks_threshold:
                    text = await asyncio.to_thread(self._decode_buffer)
                    self.silence_chunks = 0

                    if text:
                        yield text
            else:
                self.silence_chunks = 0
                self.audio_chunks.append(chunk)

        # Flush remaining audio
        if self.audio_chunks:
            text = await asyncio.to_thread(self._decode_buffer)
            if text:
                yield text

    async def close(self):
        self.audio_chunks.clear()
