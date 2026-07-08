import ast
import operator
from tools.base import BaseTool


class CalculatorTool(BaseTool):

    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @property
    def name(self):
        return "calculator"

    @property
    def description(self):
        return (
            "Perform arithmetic calculations: addition, subtraction, multiplication, division, "
            "exponentiation, modulo. Only use for numeric computations with operators +, -, *, /, **, %, //. "
            "Do NOT use for comparisons (>, <, ==) or logical checks — reason about those yourself."
        )

    def _safe_eval(self, node):
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed")
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPS:
                raise ValueError(f"Operator '{op_type.__name__}' not allowed")
            return self.ALLOWED_OPS[op_type](
                self._safe_eval(node.left),
                self._safe_eval(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPS:
                raise ValueError(f"Operator '{op_type.__name__}' not allowed")
            return self.ALLOWED_OPS[op_type](self._safe_eval(node.operand))
        else:
            raise ValueError(f"Expression type '{type(node).__name__}' not allowed")

    def execute(self, expression: str):
        try:
            tree = ast.parse(expression, mode="eval")
            result = self._safe_eval(tree.body)
            return result
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Error evaluating expression: {e}"

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
                            "description": "Arithmetic expression using only +, -, *, /, **, %, //. Example: '2+2', '10*5', '(3+4)/2'. Do NOT pass comparisons like '34>28'."
                        }
                    },
                    "required": ["expression"]
                }
            }
        }