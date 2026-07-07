class ToolRegistry():
    def __init__(self):
        self.tools = {}
    
    def register(self, tool):
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already exists")
        
        self.tools[tool.name] = tool
    
    def get(self, name):
        return self.tools[name]
         