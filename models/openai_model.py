import json
import os
from dotenv import load_dotenv

from openai import OpenAI
from models.base import Model as BaseModel
from responses import ChatResponse, ToolCall
from config import Settings

load_dotenv()


class OpenAIModel(BaseModel):
    def __init__(self):
        self.client = OpenAI()
        self.model_name = Settings.OPENAI_MODEL_NAME
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

    def chat(self, messages) -> ChatResponse:
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