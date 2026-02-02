"""
SIGNIFICANCE:
Signal analysis tool to measure peak and average amplitude of the mic input. 
Helps in determining if software Gain or Hardware levels need adjustment.
"""

import sounddevice as sd
import numpy as np

def check_levels():
    fs, duration = 16000, 5
    print(f"Recording for {duration}s...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=0)
    sd.wait()
    
    max_amp = np.max(np.abs(recording))
    print(f"Max Amplitude: {max_amp:.6f}")
    if max_amp < 0.05:
        print("Suggestion: Increase SENSITIVITY_GAIN.")

if __name__ == "__main__":
    check_levels()
