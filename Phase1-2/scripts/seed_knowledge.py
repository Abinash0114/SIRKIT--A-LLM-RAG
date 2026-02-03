"""
SIGNIFICANCE:
Initializes the RAG (Retrieval-Augmented Generation) system with baseline knowledge. 
It seeds the vector database with information about the SIRKIT project and 
general concepts to ensure the assistant has a useful starting context.
"""

from rag_engine import RAGEngine

def initialize_knowledge():
    rag = RAGEngine()
    
    # Clean up old sensitive data if it exists
    try:
        # Delete old project_phases if it exists
        rag.collection.delete(ids=["project_phases"])
        print("Cleared legacy project context.")
    except:
        pass

    # Core Identity - Generic and Safe
    rag.add_text(
        "I am SIRKIT, a local voice assistant designed for privacy and speed. "
        "I can help you manage your local files, answer questions using RAG, "
        "and assist with various tasks entirely offline.",
        doc_id="about_sirkit"
    )
    
    print("Success: RAG Reset and Seeded.")

if __name__ == "__main__":
    initialize_knowledge()
