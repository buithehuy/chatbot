import chromadb
import uuid


class VectorStore:
    def __init__(self, db_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="rag_documents")

    def is_source_indexed(self, source: str) -> bool:
        """Kiểm tra xem file đã được index chưa dựa vào metadata source."""
        results = self.collection.get(
            where={"source": source},
            limit=1
        )
        return len(results["ids"]) > 0

    def add(self, texts: list[str], embeddings: list[list[float]], metadatas: list[dict] = None):
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        payload = {
            "ids": ids,
            "embeddings": embeddings,
            "documents": texts
        }

        if metadatas is not None and len(metadatas) == len(texts):
            payload["metadatas"] = metadatas

        self.collection.add(**payload)
        print(f"Saved {len(texts)} chunks to Vector Store.")

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results["documents"][0] if results["documents"] else []
