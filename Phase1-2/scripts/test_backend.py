# Add project root to path (one level up from scripts)
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_engine import VoiceEngine
from llm_client import LLMClient
import config

def test_phase1_logic():
    print("--- Phase 1 Backend Logic Test ---")
    
    # 1. Initialize engines
    print("[1] Initializing Voice Engine...")
    voice = VoiceEngine()
    print("[2] Initializing LLM Client...")
    llm = LLMClient()
    
    # 2. Test TTS
    print("[3] Testing TTS output...")
    voice.speak("System check. I can speak.")
    
    # 3. Test Microphone and STT Fallback (No wake word)
    print("\n[4] Testing Microphone and STT...")
    print("Please say 'Hello Jarvis' in 3 seconds...")
    time.sleep(3)
    text = voice.listen_and_transcribe()
    print(f"STT Result: {text}")
    
    # 4. Test LLM if possible
    if text:
        print("\n[5] Testing LLM Chat...")
        print(f"Sending to LLM: {text}")
        try:
            response = llm.chat(text)
            print(f"LLM Response: {response}")
            voice.speak(response)
        except Exception as e:
            print(f"LLM Error: {e}")
    else:
        print("\n[!] No audio captured, skipping LLM test.")

if __name__ == "__main__":
    test_phase1_logic()
