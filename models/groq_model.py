
import json

from models.base import Model as BaseModel
from groq import Groq
from responses import ChatResponse, ToolCall

from config import Settings



client = Groq()

class GroqModel(BaseModel):
    def __init__(self):
        self.client = client
        self.model_name = Settings.GROQ_MODEL_NAME
        self.tools = []
        self._pending_tool_calls = None

    def set_tools(self, tools):
        self.tools = tools

    def convert_messages(self, messages):
        contents = []
        system_prompt = None
        for msg in messages:
            role = msg.role

            if role == "system":
                system_prompt = msg.content
                continue

            if role == "tool":
                contents.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": msg.content
                })
                continue

            if role == "assistant" and hasattr(msg, "raw_tool_calls") and msg.raw_tool_calls:
                contents.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": msg.raw_tool_calls
                })
                continue

            contents.append({
                "role": role,
                "content": msg.content
            })
        return contents, system_prompt
    
    def chat(self, messages):
        contents, system_prompt = self.convert_messages(messages)

        if system_prompt:
            contents.insert(0, {"role": "system", "content": system_prompt})

        request_kwargs = {
            "messages": contents,
            "model": self.model_name,
        }

        if self.tools:
            request_kwargs["tools"] = [tool.to_schema() for tool in self.tools]
            request_kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**request_kwargs)
        
        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            # Serialize raw tool_calls để lưu vào history đúng format Groq yêu cầu
            raw_tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
            return ChatResponse(
                tool_call=ToolCall(
                    name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments),
                    tool_call_id=tool_call.id
                ),
                raw_tool_calls=raw_tool_calls
            )
        
        return ChatResponse(content=message.content)