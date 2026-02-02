# SIRKIT - Local Intelligent Voice Assistant (Phase 1 v2)

SIRKIT is a robust, local-first voice assistant designed to run entirely on your laptop. It combines wake-word detection, speech-to-text, a local Large Language Model (LLM), and Retrieval-Augmented Generation (RAG) for persistent, context-aware intelligence.

> [!NOTE]
> This repository contains **Phase 1 (v2)** of the project, which focuses on Connectivity, Intelligence, and Memory Persistence.

## 🚀 Key Features

- **Multimodal**: Supports both "Hey Jarvis" voice triggers and direct text input via GUI.
- **Continuous Conversation**: Multi-turn interaction without repeated wake-words.
- **Persistent Memory**: Saves session history to JSON and auto-indexes interactions into a local vector database.
- **Privacy-First**: All audio processing and LLM inference (Llama 3.2 3B) happens locally on your device.

## 📁 Project Structure

This project follows a phase-centric organization:

- `Phase1-2/`: Current development unit.
  - `python/`: Core logic (Orchestrator, LLM Client, Voice Engines).
  - `scripts/`: Initialization, calibration, and diagnostic utilities.
  - `data/`: Persistent storage for conversation history and vector databases.
  - `docs/`: Technical specifications and TechStack summaries.
  - `demo/`: [Placeholder] Demo videos and assets.

## ⚙️ TechStack

- **LLM**: Ollama (Llama 3.2 3B)
- **STT**: Faster-Whisper (`base` model)
- **Wake-Word**: OpenWakeWord
- **Vector DB**: ChromaDB
- **TTS**: pyttsx3

---
*Developed for robust local intelligence and privacy.*
