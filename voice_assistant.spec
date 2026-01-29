# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Voice Assistant Pipeline
# Build with: pyinstaller voice_assistant.spec

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all provider modules
hiddenimports = [
    'providers',
    'providers.base',
    'providers.factory',
    'providers.stt_local',
    'providers.stt_deepgram',
    'providers.llm_openai',
    'providers.tts_local',
    'providers.tts_cartesia',
    'websockets',
    'aiohttp',
    'openai',
    'faster_whisper',
    'piper',
    'numpy',
    'dotenv',
]

# Collect data files
datas = [
    ('.env.example', '.'),
    ('README.md', '.'),
    ('QUICKSTART.md', '.'),
]

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceAssistantServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console window for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add your .ico file path here if you have one
)
