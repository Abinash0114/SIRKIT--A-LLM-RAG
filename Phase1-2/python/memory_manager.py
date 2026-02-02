"""
SIGNIFICANCE:
This module manages the Short-Term Memory (Session Persistence).
It stores conversation history in a local JSON file, allowing SIRKIT 
to maintain context between restarts and preventing repetitive dialogue. 
It ensures the LLM has access to recent turn-by-turn interactions.
"""

import json
import os
import config

class MemoryManager:
    def __init__(self, filename="conversation_history.json"):
        self.history_path = os.path.join(config.DATA_DIR, filename)
        os.makedirs(config.DATA_DIR, exist_ok=True)
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except: pass
        return []

    def save_history(self):
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.history, f, indent=4)
        except: pass

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 100: pass
        self.save_history()

    def get_recent_context(self, limit=10):
        return self.history[-limit:]

    def clear_history(self):
        self.history = []
        self.save_history()
