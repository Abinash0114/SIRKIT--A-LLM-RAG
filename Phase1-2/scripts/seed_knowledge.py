"""
SIGNIFICANCE:
Initializes the RAG (Retrieval-Augmented Generation) system with baseline knowledge. 
It seeds the vector database with information about the SIRKIT project and 
general concepts to ensure the assistant has a useful starting context.
"""

from rag_engine import RAGEngine

def initialize_knowledge():
    rag = RAGEngine()
    
    # Core Identity
    rag.add_text(
        "I am SIRKIT, a local voice assistant running on Llama 3.2, Faster-Whisper, and RAG.",
        doc_id="about_sirkit"
    )
    
    # Project Context
    rag.add_text(
        "The SIRKIT project is structured in phases: "
        "Phase 1: Connectivity & Core; Phase 2: Intelligence & RAG; "
        "Phase 3: Camera & Files; Phase 4: Extended Multi-Camera.",
        doc_id="project_phases"
    )

    print("Success: RAG Seeded.")

if __name__ == "__main__":
    initialize_knowledge()
