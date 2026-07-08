from rag.embedder import Embedder
from rag.vector_store import VectorStore
from rag.retriever import Retriever

embedder = Embedder()
vector_store = VectorStore(db_path="./my_knowledge_db")
retriever = Retriever(embedder, vector_store, chunk_size=150, overlap=30)

retriever.index_file("knowledge.txt")

query = "Mục tiêu của An trong tương lai là gì"
relevant_chunks = retriever.retrieve(query, top_k=3)

print("\n=== KẾT QUẢ TÌM KIẾM NGỮ NGHĨA ===")
for i, chunk in enumerate(relevant_chunks):
    print(f"\n[Đoạn {i+1}]: {chunk}")