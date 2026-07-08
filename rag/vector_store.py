import chromadb
import uuid

class VectorStore:
    def __init__(self, db_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="rag_documents")
    
    def add(self, texts: list[str], embeddings: list[list[float]], metadatas: list[dict] = None):
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        payload = {
            "ids": ids,
            "embeddings": embeddings,
            "documents": texts
        }

        if metadatas is not len(texts) and metadatas is not None:
            if any(m for m in metadatas):
                payload["metadatas"] = metadatas
        
        self.collection.add(**payload)
        
        # self.collection.add(
        #     ids=ids,
        #     embeddings=embeddings,
        #     documents=texts,
        #     metadatas=metadatas
        # )

        print(f"Save successfully {len(texts)} in Vector Store!!")

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[str]:

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return results['documents'][0] if results['documents'] else []
