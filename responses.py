from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    tool_call_id: str | None = None

@dataclass
class ChatResponse:
    content: str | None = None
    tool_call: ToolCall | None = None
    raw_tool_calls: List[dict] | None = None  # raw format để lưu vào history

