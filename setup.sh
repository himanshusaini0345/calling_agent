#!/bin/bash

# Voice Assistant Pipeline Setup Script
# This script helps you get started quickly

set -e  # Exit on error

echo "🎙️  Voice Assistant Pipeline Setup"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $python_version"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create models directory
echo "📁 Creating models directory..."
mkdir -p models
echo "✅ Models directory created"
echo ""

# Offer to download Piper model
echo "🔊 TTS Model Setup"
echo "----------------------------------"
echo "Would you like to download a Piper TTS model? (y/n)"
read -r download_piper

if [ "$download_piper" = "y" ]; then
    echo ""
    echo "Available languages:"
    echo "1) English (US) - Medium quality (recommended)"
    echo "2) Spanish (ES) - Medium quality"
    echo "3) French (FR) - Medium quality"
    echo "4) German (DE) - Medium quality"
    echo "5) Skip (I'll download manually)"
    echo ""
    echo "Enter choice (1-5):"
    read -r lang_choice
    
    case $lang_choice in
        1)
            model_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
            config_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
            model_name="en_US-lessac-medium"
            ;;
        2)
            model_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx"
            config_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
            model_name="es_ES-davefx-medium"
            ;;
        3)
            model_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx"
            config_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json"
            model_name="fr_FR-upmc-medium"
            ;;
        4)
            model_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"
            config_url="https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"
            model_name="de_DE-thorsten-medium"
            ;;
        *)
            echo "⏭️  Skipping model download"
            model_name=""
            ;;
    esac
    
    if [ -n "$model_name" ]; then
        echo ""
        echo "📥 Downloading $model_name..."
        cd models
        wget -q --show-progress "$model_url"
        wget -q --show-progress "$config_url"
        cd ..
        echo "✅ Model downloaded to models/$model_name.onnx"
        
        # Update server.py with model path
        model_path="./models/$model_name.onnx"
        echo ""
        echo "📝 Updating server.py with model path..."
        # Note: This is a simple sed replacement, may need adjustment based on exact format
        sed -i "s|\"model_path\": \"/path/to/piper/model.onnx\"|\"model_path\": \"$model_path\"|g" server.py
        echo "✅ server.py updated"
    fi
fi

echo ""
echo "🔑 API Keys Setup"
echo "----------------------------------"
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk-proj-your-key-here"
    echo ""
    echo "Optional API keys (for cloud providers):"
    echo "   DEEPGRAM_API_KEY (for cloud STT)"
    echo "   CARTESIA_API_KEY (for cloud TTS)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup Complete!"
echo "===================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OPENAI_API_KEY"
echo "2. (Optional) Update server.py with your preferred provider settings"
echo "3. Run: python3 server.py"
echo ""
echo "For detailed instructions, see:"
echo "- QUICKSTART.md - Quick start guide"
echo "- README.md - Full documentation"
echo "- ARCHITECTURE.md - System architecture"
echo ""
echo "Happy coding! 🚀"
