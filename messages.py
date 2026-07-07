from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Message:
    role: str
    content: Optional[str]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

@dataclass
class AssistantMessage:
    """Assistant message có thể kèm tool_calls (dùng cho Groq/OpenAI)."""
    role: str = "assistant"
    content: Optional[str] = None
    raw_tool_calls: Optional[List[dict]] = None
