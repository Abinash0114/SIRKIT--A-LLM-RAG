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
        
        # Security: Enforce metadata source if not provided
        final_metadata = metadata if metadata else {"source": "manual_entry"}
        
        # Security check: If metadata contains a path, ensure it's inside DATA_DIR
        if "path" in final_metadata:
            abs_path = os.path.abspath(final_metadata["path"])
            if not abs_path.startswith(os.path.abspath(config.DATA_DIR)):
                print(f"(!) Security Block: Attempted to index path outside data directory: {abs_path}")
                return

        self.collection.upsert(
            documents=[text],
            metadatas=[final_metadata],
            ids=[doc_id]
        )

    def delete_doc(self, doc_id):
        """Removes a specific document by ID."""
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            print(f"Error deleting doc {doc_id}: {e}")

    def delete_file_content(self, filename):
        """Removes all RAG entries associated with a specific filename."""
        doc_id = f"file_content_{filename}"
        self.delete_doc(doc_id)

    def rename_file_content(self, old_filename, new_filename, new_path):
        """Updates file content mapping during a rename."""
        self.delete_file_content(old_filename)
        content = self._read_file_content(new_path)
        if content:
            self.add_text(
                f"Content of file '{new_filename}':\n{content[:2000]}",
                metadata={"type": "file_content", "filename": new_filename, "path": new_path},
                doc_id=f"file_content_{new_filename}"
            )

    def _read_file_content(self, file_path):
        """Reads content from supported text files."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.txt', '.md', '.json']:
            return None
        
        try:
            # Path validation to ensure files are within DATA_DIR
            abs_file_path = os.path.abspath(file_path)
            if not abs_file_path.startswith(os.path.abspath(config.DATA_DIR)):
                print(f"(!) Security Block: Attempted to read file outside data directory: {abs_file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

    def sync_folder_contents(self, directory_path):
        """Indexes the list of files and their contents in a directory."""
        if not os.path.exists(directory_path):
            return "Folder not found."
            
        abs_dir = os.path.abspath(directory_path)
        if not abs_dir.startswith(os.path.abspath(config.DATA_DIR)):
            return "(!) Security Block: Unauthorized folder access."

        items = os.listdir(directory_path)
        folder_name = os.path.basename(directory_path)
        
        # 1. Index the list of items
        file_list_text = f"The folder '{folder_name}' contains: " + ", ".join(items)
        doc_id = f"folder_list_{folder_name}"
        self.add_text(
            file_list_text, 
            metadata={"type": "folder_listing", "path": directory_path},
            doc_id=doc_id
        )

        # 2. Index individual file contents for text files
        for item in items:
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                content = self._read_file_content(item_path)
                if content:
                    # Limit content size to avoid overloading LLM/VectorDB
                    content_to_index = content[:2000] # First 2k chars
                    self.add_text(
                        f"Content of file '{item}':\n{content_to_index}",
                        metadata={"type": "file_content", "filename": item, "path": item_path},
                        doc_id=f"file_content_{item}"
                    )
        
        return file_list_text

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
