def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("Overlap must less than chunksize")
    chunks = []
    start_idx = 0
    while start_idx < len(text) :
        end_idx = start_idx + chunk_size
        chunk = text[start_idx:end_idx]
        chunks.append(chunk)
        start_idx = start_idx + (chunk_size - overlap)
        
    return chunks


    