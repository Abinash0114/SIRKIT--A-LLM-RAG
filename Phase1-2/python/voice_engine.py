"""
SIGNIFICANCE:
The VoiceEngine is responsible for the 'Senses' of the assistant.
It handles Wake-Word detection (OpenWakeWord), Speech-to-Text (Faster-Whisper), 
and Text-to-Speech (pyttsx3) synthesis. It also implements Energy-based VAD 
(Voice Activity Detection) for smart silence clipping during transcription.
"""

import os
import sys
import threading
import numpy as np
import sounddevice as sd
from openwakeword.model import Model
from faster_whisper import WhisperModel
import pyttsx3
import config
import time

class VoiceEngine:
    def __init__(self):
        self._resolve_device_id()
        
        try:
            import openwakeword.utils
            openwakeword.utils.download_models([config.TRIGGER_WORD])
            self.ww_model = Model(wakeword_models=[config.TRIGGER_WORD], inference_framework="onnx")
        except Exception as e:
            print(f"(!) Trigger model error: {e}")
            self.ww_model = None

        # STT Initialization (base model for balance)
        self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")

        # TTS Initialization
        self.tts_engine = pyttsx3.init()
        self.tts_lock = threading.Lock()
        self.setup_tts_voice()

    def setup_tts_voice(self):
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "Zira" in voice.name or "Natural" in voice.name:
                self.tts_engine.setProperty('voice', voice.id)
                break
        self.tts_engine.setProperty('rate', 170)

    def listen_for_wake_word(self):
        if not self.ww_model: return False
        
        self.wake_detected = False
        def callback(indata, frames, time, status):
            if self.wake_detected: return
            try:
                gained_data = np.clip(indata[:, 0] * config.SENSITIVITY_GAIN, -1.0, 1.0)
                audio_int16 = (gained_data * 32768).astype(np.int16)
                if len(audio_int16) == 1280:
                    prediction = self.ww_model.predict(audio_int16)
                    for _, score in prediction.items():
                        if score > config.WAKE_WORD_THRESHOLD:
                            self.wake_detected = True
            except: pass

        try:
            with sd.InputStream(device=config.INPUT_DEVICE_ID, channels=1, samplerate=16000, 
                                blocksize=1280, callback=callback):
                while not self.wake_detected:
                    sd.sleep(100)
            return True
        except: return False

    def _resolve_device_id(self):
        if config.INPUT_DEVICE_ID is not None: return
        print("(!) Audio device ID resolution required if default fails.")

    def listen_and_transcribe(self):
        fs, chunk_size = 16000, 1024
        max_silent_chunks = int(config.SILENCE_DURATION * fs / chunk_size)
        max_total_chunks = int(20 * fs / chunk_size)
        
        recording, silent_chunks, total_chunks = [], 0, 0
        
        def callback(indata, frames, time, status):
            nonlocal silent_chunks, total_chunks
            gained_indata = np.clip(indata * config.SENSITIVITY_GAIN, -1.0, 1.0)
            recording.append(gained_indata.copy())
            if np.max(np.abs(gained_indata)) < config.SILENCE_THRESHOLD:
                silent_chunks += 1
            else: silent_chunks = 0
            total_chunks += 1

        with sd.InputStream(samplerate=fs, channels=1, device=config.INPUT_DEVICE_ID, 
                            blocksize=chunk_size, callback=callback):
            while silent_chunks < max_silent_chunks and total_chunks < max_total_chunks:
                sd.sleep(100)
        
        if not recording: return ""
        audio_data = np.concatenate(recording).flatten()
        segments, _ = self.stt_model.transcribe(audio_data, beam_size=5)
        return "".join([s.text for s in segments]).strip()

    def speak(self, text):
        with self.tts_lock:
            print(f"SIRKIT: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

if __name__ == "__main__":
    v = VoiceEngine()
    v.speak("Voice engine test.")
