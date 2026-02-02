"""
SIGNIFICANCE:
This is the main entry point and Orchestrator for the SIRKIT application. 
It manages the Tkinter-based Graphical User Interface (GUI), coordinates 
the interaction between Voice/Text inputs and the LLM/RAG backend, and 
handles threading to ensure UI responsiveness.
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
from voice_engine import VoiceEngine
from llm_client import LLMClient
import config
import time

class SirkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SIRKIT - Local Voice Assistant")
        self.root.geometry("600x400")
        self.root.configure(bg="#1e1e1e")

        self.status_var = tk.StringVar(value="Status: Initializing...")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="white", bg="#1e1e1e", font=("Arial", 10))
        self.status_label.pack(pady=(10, 0))

        self.model_label = tk.Label(root, text=f"Model: {config.LLM_MODEL}", fg="#888888", bg="#1e1e1e", font=("Arial", 8))
        self.model_label.pack(pady=(0, 10))

        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#2d2d2d", fg="#d4d4d4", font=("Consolas", 10))
        self.log_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        self.btn_frame = tk.Frame(root, bg="#1e1e1e")
        self.btn_frame.pack(pady=10)

        self.start_btn = tk.Button(self.btn_frame, text="Start Voice", command=self.start_backend, bg="#0e639c", fg="white", width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(self.btn_frame, text="Stop / Exit", command=self.exit_app, bg="#a1260d", fg="white", width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.input_frame = tk.Frame(root, bg="#1e1e1e")
        self.input_frame.pack(pady=5, padx=20, fill=tk.X)

        self.text_input = tk.Entry(self.input_frame, bg="#333333", fg="white", insertbackground="white", font=("Arial", 11))
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.text_input.bind("<Return>", lambda e: self.send_text())

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.send_text, bg="#28a745", fg="white", width=10)
        self.send_btn.pack(side=tk.RIGHT)

        self.voice = None
        self.llm = None
        self.running = False

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_backend(self):
        if self.running: return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.backend_loop, daemon=True).start()

    def backend_loop(self):
        try:
            self.status_var.set("Status: Loading Models...")
            self.log("Initializing Engines...")
            self.voice = VoiceEngine()
            self.llm = LLMClient()
            self.status_var.set("Status: Ready - Say 'Hey Jarvis'")
            self.log("SYSTEM READY")
            self.voice.speak("System initialized. I am listening.")

            while self.running:
                if self.voice.listen_for_wake_word():
                    self.status_var.set("Status: Active Session")
                    self.log("\n[!] Assistant Activated")
                    self.voice.speak("How can I help you?")
                    
                    session_active = True
                    while session_active and self.running:
                        self.status_var.set("Status: Listening...")
                        user_text = self.voice.listen_and_transcribe()
                        
                        if not user_text:
                            self.log("Session Timeout (Silence)")
                            self.voice.speak("Going to sleep. Say Hey Jarvis to wake me up again.")
                            session_active = False
                            continue

                        self.log(f"YOU: {user_text}")
                        
                        stop_phrases = ["stop", "exit", "goodbye", "thank you", "that's all"]
                        if any(phrase in user_text.lower() for phrase in stop_phrases):
                            self.voice.speak("You're welcome. Standing by.")
                            self.log("SESSION ENDED")
                            session_active = False
                            continue

                        self.status_var.set("Status: Thinking...")
                        ai_response = self.llm.chat(user_text)
                        
                        self.log(f"JARVIS: {ai_response}")
                        self.status_var.set("Status: Speaking...")
                        self.voice.speak(ai_response)
                        self.status_var.set("Status: Active Session (Listening)")
                
                self.status_var.set("Status: Ready - Say 'Hey Jarvis'")
                time.sleep(0.1)
        except Exception as e:
            self.log(f"BACKEND ERROR: {e}")
            self.running = False

    def send_text(self):
        query = self.text_input.get().strip()
        if not query: return
        
        self.text_input.delete(0, tk.END)
        self.log(f"YOU (Text): {query}")
        threading.Thread(target=self.process_text_query, args=(query,), daemon=True).start()

    def process_text_query(self, query):
        try:
            if not self.llm:
                self.log("Initializing LLM...")
                self.llm = LLMClient()
            if not self.voice:
                self.voice = VoiceEngine()

            self.status_var.set("Status: Thinking...")
            ai_response = self.llm.chat(query)
            
            self.log(f"JARVIS: {ai_response}")
            self.status_var.set("Status: Speaking...")
            self.voice.speak(ai_response)
            self.status_var.set("Status: Ready")
        except Exception as e:
            self.log(f"TEXT QUERY ERROR: {e}")
            self.status_var.set("Status: Error")

    def exit_app(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SirkitGUI(root)
    root.mainloop()
