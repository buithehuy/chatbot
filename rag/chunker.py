import re


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Chunk text bằng cách tôn trọng ranh giới câu.
    Mỗi chunk tối đa chunk_size ký tự, overlap là số ký tự giữ lại từ chunk trước.
    """
    if overlap >= chunk_size:
        raise ValueError("Overlap must be less than chunk_size")

    # Tách thành các câu dựa trên dấu câu kết thúc
    sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_parts: list[str] = []
    current_len = 0

    for sentence in sentences:
        # Nếu thêm câu này sẽ vượt chunk_size và đã có nội dung → flush
        if current_len + len(sentence) + 1 > chunk_size and current_parts:
            chunk_str = " ".join(current_parts)
            chunks.append(chunk_str)

            # Overlap: giữ lại phần cuối của chunk vừa tạo
            overlap_text = chunk_str[-overlap:] if overlap > 0 else ""
            current_parts = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)

        # Câu quá dài hơn chunk_size → cắt ký tự
        if len(sentence) > chunk_size:
            start = 0
            while start < len(sentence):
                chunks.append(sentence[start:start + chunk_size])
                start += chunk_size - overlap
            current_parts = []
            current_len = 0
        else:
            current_parts.append(sentence)
            current_len += len(sentence) + 1

    if current_parts:
        chunks.append(" ".join(current_parts))

    return chunks