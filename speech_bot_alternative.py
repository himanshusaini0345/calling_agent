"""
Alternative Speech Bot Implementation
Uses cheaper/self-hosted options:
- Faster Whisper for STT (self-hosted)
- Piper TTS for TTS (self-hosted) 
- OpenAI for LLM (you already have key)
- WebSocket transport (no Daily.co needed)
"""

import asyncio
import websockets
import json
import os
import numpy as np
from openai import AsyncOpenAI
import wave
import io

# For self-hosted STT
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Install faster-whisper: pip install faster-whisper")
    WhisperModel = None

# For self-hosted TTS
try:
    from piper.voice import PiperVoice
except ImportError:
    print("Install piper-tts: pip install piper-tts")
    PiperVoice = None


class SelfHostedSpeechBot:
    """Speech bot with self-hosted components for minimal cost"""
    
    def __init__(self):
        # OpenAI client (you already have this key)
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Faster Whisper for STT (runs locally on CPU/GPU)
        if WhisperModel:
            print("Loading Whisper model...")
            self.whisper_model = WhisperModel(
                "base",  # Options: tiny, base, small, medium, large
                device="cpu",  # Use "cuda" if you have GPU
                compute_type="int8"  # Optimize for CPU
            )
        
        # Piper for TTS (runs locally, very fast)
        if PiperVoice:
            print("Loading Piper TTS model...")
            # Download model from: https://github.com/rhasspy/piper/releases
            self.piper_voice = PiperVoice.load(
                "en_US-lessac-medium.onnx"  # You'll need to download this
            )
        
        # Conversation history
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful voice assistant. Keep responses concise and natural for speech."
            }
        ]
    
    async def speech_to_text(self, audio_data):
        """Convert speech to text using Faster Whisper"""
        if not WhisperModel:
            return "Whisper not available"
        
        # Whisper expects 16kHz mono audio
        segments, info = self.whisper_model.transcribe(
            audio_data,
            language="en",
            vad_filter=True  # Voice activity detection
        )
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    
    async def text_to_speech(self, text):
        """Convert text to speech using Piper"""
        if not PiperVoice:
            return b""
        
        # Generate speech
        audio_stream = io.BytesIO()
        self.piper_voice.synthesize(text, audio_stream)
        return audio_stream.getvalue()
    
    async def get_llm_response(self, user_message):
        """Get response from OpenAI"""
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective
            messages=self.messages,
            temperature=0.7,
            max_tokens=150  # Keep responses short for voice
        )
        
        assistant_message = response.choices[0].message.content
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    async def handle_websocket(self, websocket):
        """Handle WebSocket connection"""
        print(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                # Expect audio data as bytes
                if isinstance(message, bytes):
                    # Convert speech to text
                    text = await self.speech_to_text(message)
                    print(f"User said: {text}")
                    
                    if text:
                        # Get LLM response
                        response = await self.get_llm_response(text)
                        print(f"Bot responds: {response}")
                        
                        # Convert to speech
                        audio = await self.text_to_speech(response)
                        
                        # Send audio back
                        await websocket.send(audio)
                
                elif isinstance(message, str):
                    # Handle text messages
                    data = json.loads(message)
                    if data.get("type") == "text":
                        response = await self.get_llm_response(data["text"])
                        await websocket.send(json.dumps({
                            "type": "text",
                            "text": response
                        }))
        
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
    
    async def start_server(self, host="0.0.0.0", port=8765):
        """Start WebSocket server"""
        print(f"Starting speech bot server on ws://{host}:{port}")
        async with websockets.serve(self.handle_websocket, host, port):
            await asyncio.Future()  # Run forever


# Alternative: Using OpenAI Whisper API instead of self-hosted
class OpenAIWhisperBot:
    """Simpler version using OpenAI for both STT and LLM"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful voice assistant."
            }
        ]
    
    async def transcribe_audio(self, audio_file):
        """Use OpenAI Whisper API for transcription"""
        transcript = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return transcript.text
    
    async def generate_speech(self, text):
        """Use OpenAI TTS API"""
        response = await self.client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            speed=1.0
        )
        return response.content
    
    async def chat(self, user_message):
        """Get chat response"""
        self.messages.append({"role": "user", "content": user_message})
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            max_tokens=150
        )
        
        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message


# Run the bot
if __name__ == "__main__":
    # Choose implementation
    USE_SELF_HOSTED = False  # Set to True for self-hosted, False for OpenAI
    
    if USE_SELF_HOSTED:
        bot = SelfHostedSpeechBot()
        asyncio.run(bot.start_server())
    else:
        # Simple example using OpenAI APIs
        async def demo():
            bot = OpenAIWhisperBot()
            
            # Example text interaction
            response = await bot.chat("Hello, how are you?")
            print(f"Bot: {response}")
            
            # Generate speech
            audio = await bot.generate_speech(response)
            
            # Save to file
            with open("response.mp3", "wb") as f:
                f.write(audio)
            print("Audio saved to response.mp3")
        
        asyncio.run(demo())
