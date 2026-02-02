# SIRKIT TechStack Summary (Phase 1 v2)

The SIRKIT architecture is designed for low-latency, modularity, and 100% local operation.

## Core Backend
| Component | Technology | Significance |
| :--- | :--- | :--- |
| **Language Model** | **Ollama / Llama 3.2 3B** | Fast local inference with 128k context support. |
| **Speech-to-Text** | **Faster-Whisper (base)** | High-accuracy transcription with int8 quantization for CPU efficiency. |
| **Vector DB** | **ChromaDB** | Persistent storage for long-term associative memory. |
| **Wake Word** | **OpenWakeWord** | ONNX-based efficient trigger word detection. |

## Frontend & UI
- **Tkinter**: Lightweight, standard Python library for the main dashboard.
- **Threading**: Managed parallel execution for non-blocking UI and backend processing.

## Persistent Storage
- **JSON**: Short-term session/history serialization.
- **Parquet/SQLite (via Chroma)**: Optimized vector search indices.

## Audio Processing
- **SoundDevice**: High-fidelity stream management.
- **NumPy**: Linear algebra for digital gain and signal processing.
