import sounddevice as sd
import numpy as np
import time

def find_active_mic():
    print("=== ULTRA MIC SCANNER ===")
    print("I will now scan EVERY input device on your laptop.")
    print("Please Speak CONSTANTLY into your OnePlus Buds now...")
    time.sleep(1)
    
    devices = sd.query_devices()
    fs = 16000
    duration = 1.5
    
    best_id = -1
    max_overall_amp = 0
    
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            name = d['name']
            print(f"Checking ID {i}: {name}...", end=" ", flush=True)
            try:
                # Use small blocksize to be fast
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=i)
                sd.wait()
                amp = np.max(np.abs(recording))
                print(f"Amp: {amp:.4f}")
                if amp > max_overall_amp:
                    max_overall_amp = amp
                    best_id = i
            except Exception:
                print("Error (Skipping)")

    print("\n" + "="*30)
    if best_id != -1 and max_overall_amp > 0.005:
        print(f"WINNER: Device ID {best_id}")
        print(f"Signal Strength: {max_overall_amp:.4f}")
        print(f"Device Name: {devices[best_id]['name']}")
        print("="*30)
        print(f"\nUPDATING CONFIG TO ID {best_id}...")
        return best_id
    else:
        print("No active microphone found. Are the buds connected and active?")
        return None

if __name__ == "__main__":
    found_id = find_active_mic()
    if found_id is not None:
        # Update config.py
        import os
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.py")
        with open(config_path, "r") as f:
            lines = f.readlines()
        
        with open(config_path, "w") as f:
            for line in lines:
                if line.startswith("INPUT_DEVICE_ID ="):
                    f.write(f"INPUT_DEVICE_ID = {found_id}  # Automatically detected\n")
                else:
                    f.write(line)
        print("config.py updated successfully!")
