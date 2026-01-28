#!/usr/bin/env python3
"""
Interactive setup script for speech bot
Helps you choose the best configuration for your needs
"""

import os
import sys
import subprocess


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def install_packages(packages):
    """Install Python packages"""
    print(f"Installing: {' '.join(packages)}")
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)


def main():
    print_header("🎤 SPEECH BOT SETUP WIZARD 🤖")
    
    print("Let's set up your speech bot! Answer a few questions:\n")
    
    # Question 1: Budget
    print("1. What's your budget?")
    print("   a) $0/month (self-hosted only)")
    print("   b) <$20/month (free tiers + cheap APIs)")
    print("   c) Don't care (best quality)")
    
    budget = input("\nChoice (a/b/c): ").strip().lower()
    
    # Question 2: Speed requirement
    print("\n2. How important is speed/latency?")
    print("   a) Critical (<500ms total)")
    print("   b) Important (<1s total)")
    print("   c) Not important")
    
    speed = input("\nChoice (a/b/c): ").strip().lower()
    
    # Question 3: Setup complexity
    print("\n3. Setup complexity preference?")
    print("   a) Simplest (just OpenAI API key)")
    print("   b) Easy (cloud services, multiple API keys)")
    print("   c) Don't mind complexity (will self-host)")
    
    complexity = input("\nChoice (a/b/c): ").strip().lower()
    
    # Determine best configuration
    print_header("📊 RECOMMENDED CONFIGURATION")
    
    if budget == 'a' or complexity == 'c':
        # Self-hosted
        print("🏠 SELF-HOSTED SETUP")
        print("\nComponents:")
        print("  • STT: Faster Whisper (FREE, local)")
        print("  • TTS: Piper (FREE, local)")
        print("  • LLM: OpenAI gpt-4o-mini (you have key)")
        print("  • Transport: WebSocket (FREE)")
        print("\nCost: ~$0.005/minute (only LLM)")
        print("Latency: ~500-800ms")
        
        packages = [
            "faster-whisper",
            "piper-tts", 
            "openai",
            "websockets",
            "numpy",
            "soundfile"
        ]
        
        script = "speech_bot_alternative.py"
        
        print("\n⚙️  Additional setup:")
        print("  1. Download Piper voice model:")
        print("     wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-lessac-medium.onnx")
        print("  2. (Optional) Install Ollama for free LLM:")
        print("     curl -fsSL https://ollama.com/install.sh | sh")
        print("     ollama pull llama3.1:8b")
    
    elif complexity == 'a':
        # All OpenAI
        print("🎯 ALL OPENAI (SIMPLEST)")
        print("\nComponents:")
        print("  • STT: OpenAI Whisper API")
        print("  • TTS: OpenAI TTS")
        print("  • LLM: OpenAI gpt-4o-mini")
        print("  • Transport: WebSocket")
        print("\nCost: ~$0.03/minute")
        print("Latency: ~600-800ms")
        print("Setup: Just one API key!")
        
        packages = ["openai", "websockets"]
        script = "speech_bot_alternative.py"
    
    elif speed == 'a':
        # Ultra-fast with Groq
        print("⚡ ULTRA-FAST WITH GROQ")
        print("\nComponents:")
        print("  • STT: Deepgram (300ms)")
        print("  • TTS: Cartesia (150ms)")
        print("  • LLM: Groq (50ms for 100 tokens!)")
        print("  • Transport: Daily.co")
        print("\nCost: ~$0.015/minute")
        print("Latency: <500ms total 🚀")
        
        packages = [
            "pipecat-ai[daily,openai]",
            "deepgram-sdk",
            "cartesia",
            "groq"
        ]
        
        script = "speech_bot_groq.py"
        
        print("\n🔑 API Keys needed:")
        print("  • Groq (FREE): https://console.groq.com/")
        print("  • Deepgram ($200 free): https://console.deepgram.com/")
        print("  • Cartesia ($10 free): https://play.cartesia.ai/")
        print("  • Daily.co (FREE): https://daily.co/")
    
    else:
        # Balanced cloud setup
        print("⚖️  BALANCED CLOUD SETUP")
        print("\nComponents:")
        print("  • STT: Deepgram")
        print("  • TTS: Cartesia")
        print("  • LLM: OpenAI gpt-4o-mini")
        print("  • Transport: Daily.co")
        print("\nCost: ~$0.02/minute")
        print("Latency: ~500-700ms")
        
        packages = [
            "pipecat-ai[daily,openai]",
            "deepgram-sdk",
            "cartesia"
        ]
        
        script = "speech_bot.py"
        
        print("\n🔑 API Keys needed:")
        print("  • OpenAI (you have this!)")
        print("  • Deepgram ($200 free): https://console.deepgram.com/")
        print("  • Cartesia ($10 free): https://play.cartesia.ai/")
        print("  • Daily.co (FREE): https://daily.co/")
    
    # Install?
    print("\n" + "-" * 60)
    install = input("\nInstall required packages? (y/n): ").strip().lower()
    
    if install == 'y':
        print("\n📦 Installing packages...")
        try:
            install_packages(packages)
            print("\n✅ Installation complete!")
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            print("Try installing manually:")
            print(f"pip install {' '.join(packages)}")
            return
    
    # Create .env file
    print("\n" + "-" * 60)
    create_env = input("\nCreate .env file with your API keys? (y/n): ").strip().lower()
    
    if create_env == 'y':
        env_content = ["# Speech Bot Configuration\n"]
        
        # Always need OpenAI
        openai_key = input("\nEnter your OpenAI API key: ").strip()
        env_content.append(f"OPENAI_API_KEY={openai_key}\n")
        
        if script in ["speech_bot.py", "speech_bot_groq.py"]:
            deepgram_key = input("Enter your Deepgram API key: ").strip()
            env_content.append(f"DEEPGRAM_API_KEY={deepgram_key}\n")
            
            cartesia_key = input("Enter your Cartesia API key: ").strip()
            env_content.append(f"CARTESIA_API_KEY={cartesia_key}\n")
            
            daily_key = input("Enter your Daily.co API key: ").strip()
            env_content.append(f"DAILY_API_KEY={daily_key}\n")
        
        if script == "speech_bot_groq.py":
            groq_key = input("Enter your Groq API key: ").strip()
            env_content.append(f"GROQ_API_KEY={groq_key}\n")
        
        with open(".env", "w") as f:
            f.writelines(env_content)
        
        print("\n✅ .env file created!")
    
    # Final instructions
    print_header("🚀 YOU'RE READY!")
    print(f"Run your speech bot with:\n")
    print(f"    python {script}")
    print("\nFor more options, check:")
    print("  • README.md - Full documentation")
    print("  • PROVIDER_COMPARISON.md - All provider options")
    
    print("\n💡 Tips:")
    print("  • Start with free tiers to test")
    print("  • Monitor your API usage")
    print("  • Check the comparison guide for alternatives")
    
    print("\n📚 Resources:")
    print("  • Pipecat docs: https://docs.pipecat.ai/")
    print("  • Support: https://discord.gg/pipecat")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
