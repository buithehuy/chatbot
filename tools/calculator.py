from tools.base import BaseTool

class CalculatorTool(BaseTool):

    @property
    def name(self):
        return "calculator"

    @property
    def description(self):
        return "Perform arithmetic operations."

    def execute(self, expression):
        return eval(expression)

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Math expression like '2+2', '10*5'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }