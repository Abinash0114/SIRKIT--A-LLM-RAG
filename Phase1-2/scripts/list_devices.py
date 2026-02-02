"""
SIGNIFICANCE:
Diagnostic tool to list all available audio input and output devices. 
Essential for identifying the correct Device IDs to use in config.py.
"""

import sounddevice as sd

def list_audio_devices():
    print("Available Audio Devices:\n")
    print(sd.query_devices())

if __name__ == "__main__":
    try:
        list_audio_devices()
    except Exception as e:
        print(f"Error: {e}")
