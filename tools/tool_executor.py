from typing import Any
from responses import ToolCall


class ToolExecutor:
    def __init__(self, registry):
        self.registry = registry

    def execute(self, tool_call: Any) -> str:
        if isinstance(tool_call, ToolCall):
            tool_name = tool_call.name
            args = tool_call.arguments
        elif isinstance(tool_call, dict):
            tool_name = tool_call.get("tool") or tool_call.get("name")
            args = tool_call.get("args") or tool_call.get("arguments") or {}
        else:
            raise TypeError("tool_call must be ToolCall or dict")

        try:
            tool = self.registry.get(tool_name)
            return tool.execute(**args)
        except KeyError as e:
            return f"Tool error: {e}"
        except TypeError as e:
            return f"Tool '{tool_name}' called with wrong arguments: {e}"
        except Exception as e:
            return f"Tool '{tool_name}' execution failed: {e}"
