# Phase 1 v2 - Project Details

This document outlines the progress and implementation details of the merged Phase 1 and Phase 2.

## Implementation Overview
- **VAD (Voice Activity Detection)**: Implemented energy-based silence detection with a 1.2s trailing window.
- **Digital Gain**: Implemented 4.0x software amplification to improve mic responsiveness.
- **RAG Integration**: Conversations are auto-indexed to ensure the assistant "learns" from every interaction.
- **Session Continuity**: Implementation of `MemoryManager` to preserve context between app restarts.

## Directory Significance
- `python/`: contains the primary `main.py` entry point and logic components.
- `scripts/`: contains `calibrate_wakeword.py` to optimize trigger sensitivity.
- `data/`: contains the `SIRKIT_DATA` folder which holds the SQLite-backed vector store.
