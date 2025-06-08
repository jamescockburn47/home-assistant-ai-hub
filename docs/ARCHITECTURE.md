# System Architecture

## Design Principles
1. Offline-First: Every feature works without internet when possible
2. Modular: Each function is independent but interoperable
3. Memory-Persistent: No data or context is ever lost
4. Privacy-Focused: Local processing, no cloud dependency
5. Extensible: Easy to add new modules and capabilities

## Component Flow
Voice → Whisper.cpp → Intent Parser → Local LLM → Action Handler → Response
                                         ↓
                                    Knowledge Base
                                         ↓
                                    Home Assistant
