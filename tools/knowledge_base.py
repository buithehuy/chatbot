from tools.base import BaseTool

class KnowledgeBase(BaseTool):
    def __init__(self, retriever):
        self.retriever = retriever

    @property
    def name(self):
        return "knowledge_base"

    @property
    def description(self):
        return "Used to retrieve internal documents, confidential information, specialized knowledge, or pre-loaded text files."

    def execute(self, query: str) -> str:
        chunks = self.retriever.retrieve(query, top_k=3)
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong tài liệu nội bộ."
        return "\n---\n".join(chunks)

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A question or phrase used to search for content within a document."
                        }
                    },
                    "required": ["query"]
                }
            }
        }