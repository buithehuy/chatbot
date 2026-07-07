from typing import Any
from responses import ToolCall

class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, tool_call: Any):
        if isinstance(tool_call, ToolCall):
            tool_name = tool_call.name
            args = tool_call.arguments
        elif isinstance(tool_call, dict):
            tool_name = tool_call.get("tool") or tool_call.get("name")
            args = tool_call.get("args") or tool_call.get("arguments") or {}
        else:
            raise TypeError("tool_call must be ToolCall or dict")
        
        tool = self.registry.get(tool_name)
        return tool.execute(**args)
