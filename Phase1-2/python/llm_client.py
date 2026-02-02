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
    
    def chat(self, user_text):
        if not user_text: return ""
        
        # Long-term retrieval
        rag_context = self.rag.query(user_text)
        
        # Short-term context
        recent_history = self.memory.get_recent_context(limit=10)
        
        system_prompt = (
            "You are SIRKIT, an advanced local voice assistant. "
            "Your personality is helpful, concise, and realistic. "
            "DO NOT repeat introductory phrases like 'I am your assistant' unless specifically asked. "
            "Maintain a natural conversation flow using the history provided. "
            "If local context is provided, use it for accurate, data-driven answers."
        )
        
        if rag_context:
            system_prompt += f"\n\nRelevant Context from your memory:\n{rag_context}"

        messages = [{'role': 'system', 'content': system_prompt}]
        messages.extend(recent_history)
        messages.append({'role': 'user', 'content': user_text})

        try:
            print(f"Thinking...")
            response = ollama.chat(model=config.LLM_MODEL, messages=messages)
            ai_response = response['message']['content']
            
            # Persist turns
            self.memory.add_message('user', user_text)
            self.memory.add_message('assistant', ai_response)
            
            # Auto-index into RAG
            self.rag.add_text(
                f"Previous Interaction - User: '{user_text}' | SIRKIT: '{ai_response}'",
                metadata={"type": "conversation_history"}
            )
            
            return ai_response
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm having trouble connecting to my brain."

if __name__ == "__main__":
    client = LLMClient()
    print(client.chat("Hello!"))
