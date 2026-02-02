import sounddevice as sd
import numpy as np
import os
import sys

# Add project root to path so config can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def scan_oneplus_devices():
    devices = sd.query_devices()
    fs = 16000
    duration = 2
    
    print("Scanning OnePlus devices for audio input...")
    
    for i, d in enumerate(devices):
        if "oneplus" in d['name'].lower() and d['max_input_channels'] > 0:
            print(f"\nTesting ID {i}: {d['name']}...")
            try:
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=i)
                sd.wait()
                max_amp = np.max(np.abs(recording))
                print(f"Max Amplitude: {max_amp}")
                if max_amp > 0.01:
                    print(f"-> SUCCESS! Sound detected on ID {i}")
                else:
                    print(f"-> No sound detected on ID {i}")
            except Exception as e:
                print(f"-> Error on ID {i}: {e}")

if __name__ == "__main__":
    scan_oneplus_devices()
