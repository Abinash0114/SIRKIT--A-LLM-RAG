import sounddevice as sd
import numpy as np
import time

def test_minimal_rec():
    fs = 16000
    duration = 5
    print(f"Recording from Device 0 for {duration} seconds...")
    try:
        # Try recording into a pre-allocated array to see if memory is the issue
        recording = np.zeros((duration * fs, 1), dtype='float32')
        sd.rec(duration * fs, samplerate=fs, channels=1, device=0, out=recording)
        sd.wait()
        print(f"Recording complete. Max Amplitude: {np.max(np.abs(recording))}")
    except Exception as e:
        print(f"Recording failed: {e}")

if __name__ == "__main__":
    test_minimal_rec()
