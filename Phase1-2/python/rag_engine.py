"""
SIGNIFICANCE:
This module manages the Long-Term Memory (RAG - Retrieval-Augmented Generation).
It uses ChromaDB and Sentence-Transformers to store and retrieve contextually 
relevant information from past conversations and local data, enabling 
SIRKIT to answer questions based on its own knowledge base.
"""

import os
import chromadb
from chromadb.utils import embedding_functions
import config
import datetime

class RAGEngine:
    def __init__(self):
        self.db_path = config.VECTOR_DB_DIR
        os.makedirs(self.db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="sirkit_knowledge",
            embedding_function=self.embedding_fn
        )

    def add_text(self, text, metadata=None, doc_id=None):
        if not doc_id:
            doc_id = f"doc_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        final_metadata = metadata if metadata else {"source": "manual_entry"}
        self.collection.add(
            documents=[text],
            metadatas=[final_metadata],
            ids=[doc_id]
        )

    def query(self, query_text, n_results=3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        context = ""
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                context += f"\n--- Context {i+1} ---\n{doc}\n"
        return context.strip()

if __name__ == "__main__":
    rag = RAGEngine()
    rag.add_text("Mathematics is the study of numbers and shapes.", doc_id="math_basics")
    print(rag.query("What is maths?"))
