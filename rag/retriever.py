import os
from rag.chunker import chunk_text

class Retriever:
    def __init__(self, embedder, vector_store, chunk_size: int = 200, overlap: int = 50):
        self.embedder = embedder
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.overlap = overlap

    def index_file(self, filepath: str):
        if not os.path.exists(filepath):
            print(f"Do not find file in {filepath}")
            return
        
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"Processing {filepath} ({len(text)}) characters")
    
        chunks = chunk_text(text, self.chunk_size, self.overlap)

        if not chunks:
            print("file rong")
            return
        
        embeddings = self.embedder.embed_batch(chunks)
        
        # 4. Lưu vào vector store
        self.vector_store.add(chunks, embeddings)
        print(f"Nạp dữ liệu file {filepath} hoàn tất!")
    
    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Biến câu hỏi thành vector rồi tìm các đoạn văn bản liên quan nhất"""
        # 1. Embed câu hỏi (query) thành vector 1 chiều
        query_embedding = self.embedder.embed(query)
        
        # 2. Tìm kiếm trong vector store và trả về kết quả
        return self.vector_store.search(query_embedding, top_k=top_k)