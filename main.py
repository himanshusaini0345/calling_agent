"""
WebSocket server for real-time voice assistant
STT → (optional translation) → LLM (streaming) → TTS
Server controls audio queue & interruption.
"""

from contextlib import asynccontextmanager
import os
import asyncio
import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from transformers import AutoModel
from faster_whisper import WhisperModel

from src.data.knowledge_base import knowledge_base
from src.logging_config import setup_logging
from src.pipeline import VoicePipeline
from src.factory import ProviderFactory
from src.translators.indicTrans2 import IndicTrans2Translator

# ------------------------------------------------------------------
# ENV & LOGGING
# ------------------------------------------------------------------

load_dotenv()
setup_logging()
logger = logging.getLogger("app")

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------

HF_TOKEN = os.getenv("HF_TOKEN")

PIPELINE_CONFIG = {
    "min_tts_chars": 40,
    "max_tts_chars": 200,
    "sentence_delimiters": (".", "!", "?", ","),
    "enable_timing": True,
}

# ------------------------------------------------------------------
# INITIALIZE PROVIDERS (ONCE)
# ------------------------------------------------------------------

logger.info("🔧 Initializing providers...")

logger.info("🔧 Loading stt model")
model = AutoModel.from_pretrained("ai4bharat/indic-conformer-600m-multilingual", trust_remote_code=True)
# model = WhisperModel(
#             "base",
#             device="cpu",
#             compute_type="int8"
#         )

STT_CONFIG = {
    "provider": "indic",
    "model": model
}

stt = ProviderFactory.create_stt(**STT_CONFIG)

LLM_CONFIG = {
    "provider": "openai",
    "api_key" : os.getenv("OPENAI_API_KEY"),
    "knowledge_base": knowledge_base
}
llm = ProviderFactory.create_llm(**LLM_CONFIG)

TTS_CONFIG = {
    "provider": "piper",
    "model_path": "models/en_US-lessac-medium.onnx"
    # "provider": "azure",
    # "speech_key" : os.getenv("AZURE_SPEECH_KEY"),
    # "region" : os.getenv("AZURE_SPEECH_REGION"),
    # "voice" : "hi-IN-SwaraNeural"
}
tts = ProviderFactory.create_tts(**TTS_CONFIG)

translator = IndicTrans2Translator(hf_token=HF_TOKEN)

pipeline = VoicePipeline(
    stt=stt,
    llm=llm,
    tts=tts,
    # translator=translator,
    **PIPELINE_CONFIG
)

# ------------------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------------------

app = FastAPI()

@app.on_event("startup")
async def warmup():
    logger.info("🔥 Warming up models...")

    # 1️⃣ Warm STT (fake silence)
    dummy_audio = (b"\x00\x00" * 16000)  # 1s silence
    async def dummy_stream():
        yield dummy_audio

    async for _ in stt.transcribe_stream(dummy_stream()):
        pass

    # 2️⃣ Warm LLM
    async for _ in llm.generate_stream("hello"):
        break

    # 3️⃣ Warm TTS
    await tts.synthesize("hello")

    # 4️⃣ Warm translator
    if translator:
        translator.translate("hello")

    logger.info("✅ Warmup complete")
    
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    logger.info("🔌 Client connected")

    audio_queue: asyncio.Queue[bytes | None] = asyncio.Queue()

    # --------------------------------------------------------------
    # Callback used by VoicePipeline
    # --------------------------------------------------------------
    async def audio_callback(message_type: str, data: dict):
        """
        Pipeline → Client
        """
        if message_type == "audio_chunk":
            # Base64 encode audio bytes for browser
            audio_bytes: bytes = data["data"]
            encoded = base64.b64encode(audio_bytes)
            data = {
                "seq": data["seq"],
                "utterance_id": data["utterance_id"],
                "data": base64.b64encode(audio_bytes).decode("utf-8"),
                # "data": base64.b64encode(audio_bytes).decode("utf-8"),
            }

        await ws.send_json({
            "type": message_type,
            **data
        })

    # --------------------------------------------------------------
    # Async generator feeding audio to STT
    # --------------------------------------------------------------
    async def audio_input_stream():
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            yield chunk

    pipeline_task = asyncio.create_task(
        pipeline.run(audio_input_stream(), audio_callback)
    )

    try:
        while True:
            message = await ws.receive()
            
            if message["type"] == "websocket.disconnect":
                logger.info("🔌 WebSocket disconnect received")
                break
            
            # Raw PCM audio from browser
            if "bytes" in message:
                await audio_queue.put(message["bytes"])

            # Optional control / debug messages
            elif "text" in message:
                logger.info(f"📩 Client text: {message['text']}")

    except WebSocketDisconnect:
        logger.info("❌ Client disconnected")

    finally:
        await audio_queue.put(None)
        pipeline_task.cancel()
        await pipeline.cleanup()


