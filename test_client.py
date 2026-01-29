"""
Simple test client for the voice assistant server.
This simulates sending audio and receiving responses.
"""
import asyncio
import websockets
import json
import base64
import wave


async def test_client():
    """Simple test client that sends a WAV file and receives responses."""
    uri = "ws://localhost:9000"
    
    print("Connecting to server...")
    
    async with websockets.connect(uri) as ws:
        print("✅ Connected!")
        
        # Example: Send a test WAV file
        # In a real scenario, you'd stream microphone input
        try:
            with wave.open("test_audio.wav", "rb") as wav:
                # Verify format
                assert wav.getnchannels() == 1, "Audio must be mono"
                assert wav.getsampwidth() == 2, "Audio must be 16-bit"
                assert wav.getframerate() == 16000, "Audio must be 16kHz"
                
                print(f"📤 Sending audio ({wav.getnframes()} frames)...")
                
                # Send in chunks
                chunk_size = 1024
                while True:
                    frames = wav.readframes(chunk_size)
                    if not frames:
                        break
                    await ws.send(frames)
                    await asyncio.sleep(0.01)  # Simulate real-time streaming
                
                print("✅ Audio sent")
                
        except FileNotFoundError:
            print("❌ test_audio.wav not found")
            print("Please create a test audio file (16-bit, 16kHz, mono WAV)")
            return
        
        # Receive responses
        print("\n📥 Waiting for responses...\n")
        
        try:
            async for message in ws:
                data = json.loads(message)
                
                if data["type"] == "audio":
                    seq = data["seq"]
                    audio_data = base64.b64decode(data["data"])
                    audio_format = data.get("format", {})
                    
                    print(f"🔊 Received audio chunk #{seq}")
                    print(f"   Format: {audio_format}")
                    print(f"   Size: {len(audio_data)} bytes")
                    
                    # Save to file
                    filename = f"response_{seq}.{audio_format.get('format', 'bin')}"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"   Saved to: {filename}\n")
                    
        except websockets.exceptions.ConnectionClosed:
            print("\n🔌 Connection closed")


if __name__ == "__main__":
    asyncio.run(test_client())
