"""
SIGNIFICANCE:
Utility to verify microphone connectivity and recording quality. 
It captures 5 seconds of audio and saves it as a .wav file for manual review.
"""

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import config

def test_microphone():
    fs, duration = 16000, 5
    print(f"Recording {duration}s from device {config.INPUT_DEVICE_ID}...")
    
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=config.INPUT_DEVICE_ID)
        sd.wait()
        
        filepath = os.path.join(config.BASE_DIR, "test_mic_output.wav")
        wav.write(filepath, fs, recording)
        print(f"Saved to: {filepath}")
        
        max_amp = np.max(np.abs(recording))
        print(f"Max Amplitude: {max_amp:.4f}")
        if max_amp < 0.01:
            print("WARNING: Audio levels detected as very low.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_microphone()
