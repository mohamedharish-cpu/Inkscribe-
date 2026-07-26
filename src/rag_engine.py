import chromadb
from chromadb.utils import embedding_functions

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Splits long text documents into overlapping chunks for precise vector retrieval."""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        
    return chunks

class RAGEngine:
    def __init__(self, collection_name: str = "inkscribe_knowledge_base"):
        # In-Memory ChromaDB Vector Client
        self.client = chromadb.Client()
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Reset collection if exists to ensure clean state per upload
        try:
            self.client.delete_collection(name=collection_name)
        except Exception:
            pass
            
        self.collection = self.client.create_collection(
            name=collection_name, 
            embedding_function=self.emb_fn
        )

    def add_documents(self, parsed_docs: dict):
        """
        Takes parsed docs dict {'filename.pdf': 'text...'} 
        and indexes chunks into ChromaDB.
        """
        documents = []
        metadatas = []
        ids = []
        
        counter = 0
        for filename, full_text in parsed_docs.items():
            chunks = chunk_text(full_text)
            for idx, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({"source": filename, "chunk_index": idx})
                ids.append(f"{filename}_chunk_{idx}_{counter}")
                counter += 1
                
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return len(documents)
        return 0

    def query_context(self, query: str, top_k: int = 6) -> str:
        """
        Retrieves top relevant document chunks for a given prompt query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        retrieved_text = []
        if results and "documents" in results and results["documents"]:
            for docs in results["documents"]:
                retrieved_text.extend(docs)
                
        return "\n\n--- RELEVANT CONTEXT ---\n\n".join(retrieved_text)