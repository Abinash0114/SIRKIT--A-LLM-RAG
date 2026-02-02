import sounddevice as sd

target_name = "oneplus nord buds 3 pro"

print(f"Searching for device: {target_name}...")

devices = sd.query_devices()
found_input = None
found_output = None

for i, device in enumerate(devices):
    name = device['name'].lower()
    # Check if name contains our target
    if target_name in name:
        # Check input/output channels
        if device['max_input_channels'] > 0:
            found_input = i
            print(f"Found Input Device: ID {i} - {device['name']}")
        if device['max_output_channels'] > 0:
            found_output = i
            print(f"Found Output Device: ID {i} - {device['name']}")

if found_input is not None:
    print(f"RECOMMENDED_INPUT_ID={found_input}")
else:
    print("No input device found matching the name.")

if found_output is not None:
    print(f"RECOMMENDED_OUTPUT_ID={found_output}")
else:
    print("No output device found matching the name.")
