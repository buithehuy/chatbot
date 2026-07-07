from typing import Any

class Tool():
    def __init__(self, name, description, parameters, function):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function

    
    def execute(self, **kwargs) -> Any :
        return self.function(**kwargs)
        
    
    def to_schema(self) -> dict :
        return ({"name": self.name,
                 "description": self.description,
                 "parameters": self.parameters})
    
