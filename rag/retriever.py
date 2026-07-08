import os
from rag.chunker import chunk_text


class Retriever:
    def __init__(self, embedder, vector_store, chunk_size: int = 500, overlap: int = 50):
        self.embedder = embedder
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.overlap = overlap

    def index_file(self, filepath: str):
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return

        source = os.path.abspath(filepath)

        # Kiểm tra đã index chưa để tránh duplicate dữ liệu
        if self.vector_store.is_source_indexed(source):
            print(f"File '{filepath}' already indexed, skipping.")
            return

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"Processing '{filepath}' ({len(text)} characters)...")

        chunks = chunk_text(text, self.chunk_size, self.overlap)
        if not chunks:
            print("File is empty, nothing to index.")
            return

        embeddings = self.embedder.embed_batch(chunks)
        metadatas = [{"source": source} for _ in chunks]

        self.vector_store.add(chunks, embeddings, metadatas=metadatas)
        print(f"Indexed '{filepath}' successfully ({len(chunks)} chunks).")

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Embed câu hỏi rồi tìm các đoạn văn bản liên quan nhất."""
        query_embedding = self.embedder.embed(query)
        return self.vector_store.search(query_embedding, top_k=top_k)