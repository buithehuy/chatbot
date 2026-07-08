class ToolRegistry():
    def __init__(self):
        self.tools = {}

    def register(self, tool):
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already exists")
        self.tools[tool.name] = tool

    def get(self, name: str):
        if name not in self.tools:
            available = list(self.tools.keys())
            raise KeyError(
                f"Tool '{name}' not found. Available tools: {available}"
            )
        return self.tools[name]