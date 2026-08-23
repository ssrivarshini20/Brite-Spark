from app.rag.embeddings import embedding_service
from typing import List, Dict, Any
from datetime import date

class Retriever:
    def __init__(self, top_k: int = 5, distance_threshold: float = 1.2):
        self.top_k = top_k
        self.distance_threshold = distance_threshold

    def retrieve(self, query: str, claim_date: date | None = None) -> List[Dict[str, Any]]:
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
                distance = results["distances"][0][i]
                metadata["distance"] = distance
                effective_from = metadata.get("effective_from")
                if effective_from and (claim_date is None or date.fromisoformat(effective_from) > claim_date):
                    continue
                if distance <= self.distance_threshold:
                    retrieved_chunks.append(metadata)
                
        return retrieved_chunks

    def get_collection_size(self) -> int:
        return embedding_service.collection.count()

retriever = Retriever(top_k=7)
