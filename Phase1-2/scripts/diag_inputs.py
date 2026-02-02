import sounddevice as sd
print("Index | Inputs | Name")
for i, d in enumerate(sd.query_devices()):
    if d['max_input_channels'] > 0:
        print(f"{i:5} | {d['max_input_channels']:6} | {d['name']}")
