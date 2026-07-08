import json
from google import genai
from google.genai import types
from models.base import Model as BaseModel
from responses import ChatResponse, ToolCall
from config import Settings


class GeminiModel(BaseModel):
    def __init__(self):
        self.client = genai.Client()
        self.model_name = Settings.GEMINI_MODEL_NAME
        self.tools = []

    def set_tools(self, tools):
        self.tools = tools

    def _build_gemini_tools(self):
        """Chuyển đổi tool schema từ OpenAI format sang Gemini FunctionDeclaration."""
        declarations = []
        for tool in self.tools:
            schema = tool.to_schema()["function"]
            declarations.append(
                types.FunctionDeclaration(
                    name=schema["name"],
                    description=schema["description"],
                    parameters=schema.get("parameters")
                )
            )
        return [types.Tool(function_declarations=declarations)]

    def convert_messages(self, messages):
        contents = []
        system_prompt = None

        for msg in messages:
            role = msg.role

            if role == "system":
                system_prompt = msg.content
                continue

            if role == "assistant":
                if hasattr(msg, "raw_tool_calls") and msg.raw_tool_calls:
                    # Tái tạo function_call parts từ raw_tool_calls (Gemini format)
                    parts = []
                    for tc in msg.raw_tool_calls:
                        args = tc.get("args", {})
                        parts.append(types.Part(
                            function_call=types.FunctionCall(name=tc["name"], args=args)
                        ))
                    contents.append(types.Content(role="model", parts=parts))
                else:
                    contents.append(types.Content(
                        role="model",
                        parts=[types.Part(text=msg.content or "")]
                    ))
                continue

            if role == "tool":
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(
                        function_response=types.FunctionResponse(
                            name=msg.name,
                            response={"result": msg.content}
                        )
                    )]
                ))
                continue

            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg.content or "")]
            ))

        return contents, system_prompt

    def chat(self, messages) -> ChatResponse:
        contents, system_prompt = self.convert_messages(messages)

        config_kwargs = {}
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt
        if self.tools:
            config_kwargs["tools"] = self._build_gemini_tools()

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs)
        )

        # Kiểm tra function calls
        if response.function_calls:
            tool_calls = [
                ToolCall(
                    name=fc.name,
                    arguments=dict(fc.args),
                    tool_call_id=fc.name  # Gemini không có ID, dùng tên thay thế
                )
                for fc in response.function_calls
            ]
            # Lưu raw_tool_calls theo Gemini format
            raw_tool_calls = [
                {"name": fc.name, "args": dict(fc.args)}
                for fc in response.function_calls
            ]
            return ChatResponse(
                tool_call=tool_calls[0],
                tool_calls=tool_calls,
                raw_tool_calls=raw_tool_calls
            )

        return ChatResponse(content=response.text)