"""
SIGNIFICANCE:
Utility to calibrate the 'hey_jarvis' wake-word detection. 
It prints real-time probability scores to help users determine 
the best WAKE_WORD_THRESHOLD for their environment.
"""

import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import config

def calibrate():
    try:
        model = Model(wakeword_models=[config.TRIGGER_WORD], inference_framework="onnx")
    except:
        print("Model load failed.")
        return

    def callback(indata, frames, time, status):
        gained_data = np.clip(indata[:, 0] * config.SENSITIVITY_GAIN, -1.0, 1.0)
        audio_int16 = (gained_data * 32768).astype(np.int16)
        
        if len(audio_int16) == 1280:
            prediction = model.predict(audio_int16)
            for name, score in prediction.items():
                bar = "#" * int(score * 50)
                print(f"[{name}] {score:.4f} | {bar.ljust(50)}", end='\r')

    print(f"Calibrating: Say '{config.WAKE_WORD}'...")
    with sd.InputStream(device=config.INPUT_DEVICE_ID, channels=1, samplerate=16000, 
                        blocksize=1280, callback=callback):
        while True: sd.sleep(100)

if __name__ == "__main__":
    calibrate()
