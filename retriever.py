from app.rag.embeddings import embedding_service
from typing import List, Dict, Any

class Retriever:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        # Get query embedding
        query_embedding = embedding_service.embed_text(query)
        
        # Search ChromaDB
        results = embedding_service.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        retrieved_chunks = []
        if results["metadatas"] and results["metadatas"][0]:
            for i, metadata in enumerate(results["metadatas"][0]):
                # Add distance if useful for debugging
                metadata["distance"] = results["distances"][0][i]
                retrieved_chunks.append(metadata)
                
        return retrieved_chunks

retriever = Retriever(top_k=7)
