"""
SIGNIFICANCE:
Central configuration hub for SIRKIT. 
Contains system-wide constants, device IDs, sensitivity thresholds, 
LLM settings, and directory path management. 
"""

import os

# Audio Connectivity
INPUT_DEVICE_ID = 0  # Microsoft Sound Mapper
SENSITIVITY_GAIN = 4.0

# Detection & Conversation Logic
WAKE_WORD = "Jarvis"
TRIGGER_WORD = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.25
SILENCE_THRESHOLD = 0.003

# LLM Backend
LLM_MODEL = "llama3.2:3b"
LLM_HOST = "http://localhost:11434"

# Path Management
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Data is now stored in the sibling 'data' directory
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data", "SIRKIT_DATA"))
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")
