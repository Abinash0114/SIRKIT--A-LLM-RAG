"""
SIGNIFICANCE:
This module acts as the 'Brain' of SIRKIT. 
It facilitates communication with the local Ollama LLM (Llama 3.2 3B). 
It integrates Short-Term Memory (session history) and Long-Term Memory (RAG) 
to provide context-aware, realistic, and persistent responses.
"""

import ollama
import config
from rag_engine import RAGEngine
from memory_manager import MemoryManager

class LLMClient:
    def __init__(self):
        self.rag = RAGEngine()
        self.memory = MemoryManager()
        self.current_files_context = "" # Live context from GUI

    def set_files_context(self, context_text):
        self.current_files_context = context_text
    
    def chat(self, user_text):
        if not user_text: return ""
        
        # Performance: Skip RAG for tiny/generic queries
        rag_context = ""
        if len(user_text.split()) > 3:
            rag_context = self.rag.query(user_text)
        
        # Short-term context
        recent_history = self.memory.get_recent_context(limit=5) # Reduced limit for speed
        
        system_prompt = (
            "You are SIRKIT, a lightning-fast local voice assistant. "
            "Be extremely concise. Use 1-2 short sentences unless detail is requested. "
            "Your personality is sharp, helpful, and realistic. "
            "Current Local UI state: " + (self.current_files_context if self.current_files_context else "No files visible.")
        )
        
        if rag_context:
            system_prompt += f"\n\nLocal Knowledge:\n{rag_context}"

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(recent_history)
        messages.append({'role': 'user', 'content': user_text})

        try:
            # options can help with speed/performance depending on backend
            response = ollama.chat(
                model=config.LLM_MODEL, 
                messages=messages,
                options={"temperature": 0.5, "num_predict": 100} # limit prediction for speed
            )
            ai_response = response['message']['content']
            
            # Persist turns (do this in background if possible, but for now just kept here)
            self.memory.add_message('user', user_text)
            self.memory.add_message('assistant', ai_response)
            
            # Index only meaningful interactions
            if len(user_text) > 10:
                self.rag.add_text(
                    f"Interaction: {user_text} -> {ai_response}",
                    metadata={"type": "memory"}
                )
            
            return ai_response
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Brain sync error. Check Ollama."

if __name__ == "__main__":
    client = LLMClient()
    print(client.chat("Hello!"))
