import json

from groq import BadRequestError
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

            contents.append({"role": role, "content": msg.content})

        return contents, system_prompt

    def _call_api(self, contents, system_prompt, use_tools: bool = True) -> ChatResponse:
        """Gọi Groq API. Nếu use_tools=False, bỏ qua tools để tránh tool_use_failed."""
        if system_prompt:
            contents = [{"role": "system", "content": system_prompt}] + contents

        request_kwargs = {
            "messages": contents,
            "model": self.model_name,
        }

        if use_tools and self.tools:
            request_kwargs["tools"] = [tool.to_schema() for tool in self.tools]
            request_kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**request_kwargs)
        message = response.choices[0].message

        if message.tool_calls:
            tool_calls = [
                ToolCall(
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                    tool_call_id=tc.id
                )
                for tc in message.tool_calls
            ]
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
                tool_call=tool_calls[0],
                tool_calls=tool_calls,
                raw_tool_calls=raw_tool_calls
            )

        return ChatResponse(content=message.content)

    def chat(self, messages) -> ChatResponse:
        contents, system_prompt = self.convert_messages(messages)

        try:
            return self._call_api(contents, system_prompt, use_tools=True)

        except BadRequestError as e:
            error_body = e.body if hasattr(e, "body") else {}
            code = error_body.get("error", {}).get("code", "")

            if code == "tool_use_failed":
                # Model sinh tool call JSON bị lỗi → retry không dùng tools
                print(f"\033[91m⚠ tool_use_failed — retrying without tools...\033[0m")
                return self._call_api(contents, system_prompt, use_tools=False)

            raise  # lỗi khác thì vẫn raise