# Phase 3 - Camera & Vision Integration

This document outlines the progress and implementation details of Phase 3, building upon the foundations of Phase 1 and 2.

## Implementation Overview
- **Vision Engine**: Integrated `OpenCV` for real-time camera access, persistent video sessions, and frame capture.
- **Active File Monitoring**: Implemented `watchfiles` to detect file system changes (add/delete/modify) and automatically sync them with the RAG engine in real-time.
- **Remote Camera Control**: Added ability to control camera via text commands in addition to voice ("capture", "click", "decapture").
- **Drag & Drop**: Enhanced GUI with `tkinterdnd2` to allow dragging files directly into the assistant's workspace.
- **VAD & Audio**: Continued refinement of Voice Activity Detection and digital gain (4.0x) for robust hearing.

## Directory Significance
- `python/`: 
    - `camera_engine.py`: Handles webcam sessions and image saving.
    - `file_monitor.py`: Watches for file changes and triggers RAG updates.
    - `main.py`: Updated GUI and orchestrator logic.
- `scripts/`: Diagnostic tools including `calibrate_wakeword.py` and `list_devices.py`.
- `data/`: Central storage (`SIRKIT_DATA`) for images, vector DB, and logs.

