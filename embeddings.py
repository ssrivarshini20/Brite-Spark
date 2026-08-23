import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name="policy_manual",
            metadata={"hnsw:space": "cosine"}
        )

    def embed_text(self, text: str) -> list[float]:
        # Generate embedding for a single text
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Generate embeddings for a batch of texts
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def index_chunks(self, chunks: list[dict]):
        # Index chunks into ChromaDB
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        # Process in batches to avoid memory issues if large
        texts = [chunk["source_text"] for chunk in chunks]
        batch_embeddings = self.embed_batch(texts)

        for i, chunk in enumerate(chunks):
            ids.append(f"{chunk['document']}:{chunk['clause']}")
            documents.append(chunk["source_text"])
            metadatas.append({
                "document": chunk["document"],
                "section": chunk["section"],
                "clause": chunk["clause"],
                "source_text": chunk["source_text"],
                "effective_from": chunk.get("effective_from") or "",
                "is_amendment": str(chunk.get("is_amendment", False)).lower()
            })
            embeddings.append(batch_embeddings[i])

        # Upsert to ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

embedding_service = EmbeddingService()
