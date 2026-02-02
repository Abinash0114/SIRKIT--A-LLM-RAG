# SIRKIT- A_LLM_RAG
A high-performance, privacy-first local voice assistant powered by Llama 3.2, Faster-Whisper, and RAG. Features persistent conversation memory and multimodal (voice/text) input, running entirely on-device for maximum speed and security
SIRKIT is a sophisticated, privacy-centric voice assistant designed to operate entirely on local hardware. By leveraging state-of-the-art local LLMs, quantized speech-to-text models, and persistent vector databases, SIRKIT provides an intelligent, context-aware experience without the need for internet connectivity or third-party API keys.

> [!IMPORTANT]
> This repository represents the **Phase 1 (v2)** implementation, uniting core connectivity, memory persistence, and RAG intelligence into a professional, production-ready structure.

---

## 🚀 Key Features

- **Multimodal Interaction**: Seamlessly switch between "Hey Jarvis" voice activation and a responsive text-based GUI.
- **Persistent Long-Term Memory (RAG)**: Automatically indexes every conversation turn into a local ChromaDB instance, allowing the assistant to recall historical context across sessions.
- **Short-Term Session Memory**: maintains the last 10 turns of conversation in real-time history for coherent, multi-turn dialogue.
- **Turbo-Sensitive Wake-Word**: Optimized ONNX models with 4x software gain ensure reliable "Hey Jarvis" detection even in noisy environments.
- **Noisy Silence Detection (VAD)**: Energy-based Voice Activity Detection dynamically clips audio segments, improving transcription speed and accuracy.
- **Privacy Core**: 100% of audio and text data remains on your machine.

---

## 🧠 The Intelligence: System Prompt

SIRKIT's personality and logic are governed by a strictly defined system prompt to ensure helpfulness, realism, and efficiency.

```text
You are SIRKIT, an advanced local voice assistant. 
Your personality is helpful, concise, and realistic. 
DO NOT repeat introductory phrases like 'I am your assistant' unless specifically asked. 
Maintain a natural conversation flow using the history provided. 
If local context is provided, use it for accurate, data-driven answers.
```

---

## ⚙️ TechStack Architecture

| Component | Technology | Implementation Details |
| :--- | :--- | :--- |
| **Brain (LLM)** | **Ollama / Llama 3.2 3B** | Fast CPU inference using 4-bit quantization. |
| **Hearing (STT)** | **Faster-Whisper** | `base` model with `int8` compute for a balance of speed and accuracy. |
| **Voice (TTS)** | **pyttsx3** | Native SAPI5/NSSpeechSynthesizer integration for zero-latency speech. |
| **Memory (RAG)** | **ChromaDB** | High-performance vector store with `SentenceTransformer` embeddings. |
| **Triggers (WW)** | **OpenWakeWord** | ONNX-driven detection for "Hey Jarvis". |
| **Interface** | **Tkinter** | Standard Python GUI with non-blocking threaded backend. |

---

## 📁 Repository Structure

```text
Phase1-2/
├── python/           # Core Orchestrator & Backend Logic
│   ├── main.py           # GUI & Main Initialization
│   ├── llm_client.py     # Ollama & RAG Integration
│   ├── voice_engine.py   # STT, TTS, and Wake-Word Logic
│   ├── memory_manager.py # JSON-based Session Persistence
│   ├── rag_engine.py     # ChromaDB Vector Management
│   └── config.py         # System-wide Configuration
├── scripts/          # Diagnostic & Setup Utilities
│   ├── calibrate_wakeword.py # Real-time trigger score visualizer
│   ├── list_devices.py      # Audio hardware scanner
│   ├── test_mic.py         # 5-second recording quality test
│   └── seed_knowledge.py   # RAG database initialization
├── data/             # Persistent Storage (SIRKIT_DATA)
│   ├── conversation_history.json
│   └── vector_db/        # SQLite/Parquet Vector Store
├── docs/             # Technical Documentation
└── demo/             # Video walkthroughs (.zip archives)
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (installed and running)
- `Llama 3.2 3B` model pulled: `ollama pull llama3.2`

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Abinash0114/SIRKIT--A-LLM-RAG.git

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Audio Configuration
Run the following script to identify your microphone ID:
```bash
python Phase1-2/scripts/list_devices.py
```
Update `INPUT_DEVICE_ID` in `Phase1-2/python/config.py` accordingly.

---

## 🎮 Usage

1. **Initialize RAG**: `python Phase1-2/scripts/seed_knowledge.py`
2. **Launch Assistant**: `python Phase1-2/python/main.py`
3. **Calibrate (Optional)**: If the wake-word is too quiet, run `python Phase1-2/scripts/calibrate_wakeword.py` to tune sensitivity.

---

*SIRKIT - Developing Local Intelligence, One Phase at a Time.*

