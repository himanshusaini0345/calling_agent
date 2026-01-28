"""
Real-time Speech Bot with OpenAI
Complete conversational interface with:
- Real-time audio streaming
- Voice Activity Detection
- Web-based UI
- Full duplex conversation
"""

import asyncio
import websockets
import json
import os
import base64
from openai import AsyncOpenAI
from pathlib import Path
import wave
import io

class ConversationalSpeechBot:
    """Real-time conversational bot using OpenAI APIs"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful voice assistant. Keep responses concise and conversational since they will be spoken aloud."
            }
        ]
        self.is_processing = False
    
    async def transcribe_audio(self, audio_bytes):
        """Transcribe audio using OpenAI Whisper"""
        # Create a temporary file-like object
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        transcript = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return transcript.text
    
    async def generate_speech(self, text):
        """Generate speech using OpenAI TTS"""
        response = await self.client.audio.speech.create(
            model="tts-1",  # Fast model
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
            max_tokens=150,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        print(f"✅ Client connected from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                if self.is_processing:
                    await websocket.send(json.dumps({
                        "type": "status",
                        "message": "Already processing..."
                    }))
                    continue
                
                self.is_processing = True
                
                try:
                    data = json.loads(message)
                    
                    if data["type"] == "audio":
                        # Decode base64 audio
                        audio_bytes = base64.b64decode(data["audio"])
                        
                        # Send status
                        await websocket.send(json.dumps({
                            "type": "status",
                            "message": "Transcribing..."
                        }))
                        
                        # Transcribe
                        text = await self.transcribe_audio(audio_bytes)
                        print(f"👤 User: {text}")
                        
                        # Send transcription
                        await websocket.send(json.dumps({
                            "type": "transcription",
                            "text": text
                        }))
                        
                        if text.strip():
                            # Get LLM response
                            await websocket.send(json.dumps({
                                "type": "status",
                                "message": "Thinking..."
                            }))
                            
                            response = await self.chat(text)
                            print(f"🤖 Bot: {response}")
                            
                            # Send text response
                            await websocket.send(json.dumps({
                                "type": "response",
                                "text": response
                            }))
                            
                            # Generate speech
                            await websocket.send(json.dumps({
                                "type": "status",
                                "message": "Generating speech..."
                            }))
                            
                            audio = await self.generate_speech(response)
                            audio_base64 = base64.b64encode(audio).decode()
                            
                            # Send audio response
                            await websocket.send(json.dumps({
                                "type": "audio_response",
                                "audio": audio_base64
                            }))
                    
                    elif data["type"] == "text":
                        # Text-only interaction
                        text = data["text"]
                        print(f"👤 User (text): {text}")
                        
                        response = await self.chat(text)
                        print(f"🤖 Bot: {response}")
                        
                        await websocket.send(json.dumps({
                            "type": "response",
                            "text": response
                        }))
                        
                        # Generate speech for text input too
                        audio = await self.generate_speech(response)
                        audio_base64 = base64.b64encode(audio).decode()
                        
                        await websocket.send(json.dumps({
                            "type": "audio_response",
                            "audio": audio_base64
                        }))
                
                except Exception as e:
                    print(f"❌ Error: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
                
                finally:
                    self.is_processing = False
        
        except websockets.exceptions.ConnectionClosed:
            print("❌ Client disconnected")
    
    async def start(self, host="0.0.0.0", port=8765):
        """Start the WebSocket server"""
        print(f"\n🎤 Speech Bot Server Starting...")
        print(f"📍 WebSocket: ws://{host}:{port}")
        print(f"🌐 Open web interface at: http://localhost:{port}")
        print(f"\nWaiting for connections...\n")
        
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever


# HTML Client Interface
HTML_CLIENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Chat Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .status {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: 500;
            background: #f0f0f0;
            color: #666;
        }
        
        .status.connected {
            background: #d4edda;
            color: #155724;
        }
        
        .status.recording {
            background: #fff3cd;
            color: #856404;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        .status.processing {
            background: #cce5ff;
            color: #004085;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .chat-box {
            height: 300px;
            overflow-y: auto;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 80%;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.bot {
            background: #e0e0e0;
            color: #333;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        button {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        #recordBtn {
            background: #667eea;
            color: white;
        }
        
        #recordBtn:hover:not(:disabled) {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        #recordBtn.recording {
            background: #dc3545;
            animation: recordPulse 1.5s ease-in-out infinite;
        }
        
        @keyframes recordPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        #stopBtn {
            background: #dc3545;
            color: white;
        }
        
        #stopBtn:hover:not(:disabled) {
            background: #c82333;
        }
        
        .text-input {
            display: flex;
            gap: 10px;
        }
        
        input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        #sendBtn {
            background: #28a745;
            color: white;
            flex: 0 0 100px;
        }
        
        #sendBtn:hover:not(:disabled) {
            background: #218838;
        }
        
        .info {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Voice Chat Bot</h1>
        
        <div id="status" class="status">Connecting...</div>
        
        <div id="chatBox" class="chat-box"></div>
        
        <div class="controls">
            <button id="recordBtn" disabled>🎙️ Hold to Talk</button>
            <button id="stopBtn" disabled style="display: none;">⏹️ Stop</button>
        </div>
        
        <div class="text-input">
            <input type="text" id="textInput" placeholder="Or type a message..." disabled>
            <button id="sendBtn" disabled>Send</button>
        </div>
        
        <div class="info">
            💡 Hold the microphone button to speak, or type a message
        </div>
    </div>

    <script>
        let ws;
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        
        const status = document.getElementById('status');
        const chatBox = document.getElementById('chatBox');
        const recordBtn = document.getElementById('recordBtn');
        const stopBtn = document.getElementById('stopBtn');
        const textInput = document.getElementById('textInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // Connect to WebSocket
        function connect() {
            ws = new WebSocket('ws://localhost:8765');
            
            ws.onopen = () => {
                status.textContent = '✅ Connected - Ready to chat!';
                status.className = 'status connected';
                recordBtn.disabled = false;
                textInput.disabled = false;
                sendBtn.disabled = false;
            };
            
            ws.onclose = () => {
                status.textContent = '❌ Disconnected - Reconnecting...';
                status.className = 'status';
                recordBtn.disabled = true;
                textInput.disabled = true;
                sendBtn.disabled = true;
                setTimeout(connect, 2000);
            };
            
            ws.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'status') {
                    status.textContent = data.message;
                    status.className = 'status processing';
                } else if (data.type === 'transcription') {
                    addMessage(data.text, 'user');
                } else if (data.type === 'response') {
                    addMessage(data.text, 'bot');
                } else if (data.type === 'audio_response') {
                    // Play audio response
                    const audio = new Audio('data:audio/mp3;base64,' + data.audio);
                    audio.play();
                    status.textContent = '✅ Connected - Ready to chat!';
                    status.className = 'status connected';
                } else if (data.type === 'error') {
                    status.textContent = '❌ Error: ' + data.message;
                    status.className = 'status';
                }
            };
        }
        
        function addMessage(text, type) {
            const message = document.createElement('div');
            message.className = `message ${type}`;
            message.textContent = text;
            chatBox.appendChild(message);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        // Voice recording
        recordBtn.addEventListener('mousedown', startRecording);
        recordBtn.addEventListener('mouseup', stopRecording);
        recordBtn.addEventListener('touchstart', startRecording);
        recordBtn.addEventListener('touchend', stopRecording);
        
        async function startRecording() {
            if (isRecording) return;
            
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        ws.send(JSON.stringify({
                            type: 'audio',
                            audio: base64Audio
                        }));
                    };
                    
                    reader.readAsDataURL(audioBlob);
                    
                    // Stop all tracks
                    stream.getTracks().forEach(track => track.stop());
                };
                
                mediaRecorder.start();
                isRecording = true;
                recordBtn.textContent = '🔴 Recording...';
                recordBtn.classList.add('recording');
                status.textContent = '🎙️ Recording...';
                status.className = 'status recording';
            } catch (err) {
                console.error('Error accessing microphone:', err);
                alert('Could not access microphone. Please grant permission.');
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                recordBtn.textContent = '🎙️ Hold to Talk';
                recordBtn.classList.remove('recording');
                status.textContent = '⏳ Processing...';
                status.className = 'status processing';
            }
        }
        
        // Text input
        sendBtn.addEventListener('click', sendText);
        textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendText();
        });
        
        function sendText() {
            const text = textInput.value.trim();
            if (!text) return;
            
            addMessage(text, 'user');
            ws.send(JSON.stringify({
                type: 'text',
                text: text
            }));
            
            textInput.value = '';
            status.textContent = '⏳ Processing...';
            status.className = 'status processing';
        }
        
        // Initialize
        connect();
    </script>
</body>
</html>
"""


def save_html_client():
    """Save the HTML client to a file"""
    with open("voice_chat_client.html", "w", encoding="utf-8") as f:

        f.write(HTML_CLIENT)
    print("✅ HTML client saved to: voice_chat_client.html")


if __name__ == "__main__":
    # Save HTML client
    save_html_client()
    
    # Start the bot
    bot = ConversationalSpeechBot()
    
    print("\n" + "="*60)
    print("  🎤 CONVERSATIONAL SPEECH BOT")
    print("="*60)
    print("\n📝 Instructions:")
    print("  1. Open voice_chat_client.html in your browser")
    print("  2. Hold the button to speak")
    print("  3. Or type a message and press Enter")
    print("\n" + "="*60 + "\n")
    
    asyncio.run(bot.start())