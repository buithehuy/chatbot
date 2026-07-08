from messages import Message, AssistantMessage
from tools.tool_executor import ToolExecutor
from config import Settings


class ChatBot:
    def __init__(self, model, tool_executor=None):
        self.model = model
        self.tool_executor = tool_executor
        self.system_prompt = Settings.SYSTEM_PROMPT
        self.history = []

        if tool_executor:
            tools_list = list(tool_executor.registry.tools.values())
            self.model.set_tools(tools_list)

    def chat(self, user_input: str) -> str:
        self.history.append(Message(role="user", content=user_input))
        max_steps = 5
        step = 0

        while step < max_steps:
            step += 1
            messages = [Message(role="system", content=self.system_prompt), *self.history]
            response = self.model.chat(messages)

            # Không có tool call → trả lời cuối cùng
            if not response.tool_calls:
                self.history.append(Message(role="assistant", content=response.content))
                return response.content if response.content is not None else ""

            # Có tool calls → thực thi TẤT CẢ tool calls trong lượt này
            self.history.append(
                AssistantMessage(content=None, raw_tool_calls=response.raw_tool_calls)
            )

            for tc in response.tool_calls:
                print(f"\n\033[93m⚙ Tool call:\033[0m \033[96m{tc.name}\033[0m  args={tc.arguments}")
                tool_result = self.tool_executor.execute(tc)
                print(f"\033[93m⚙ Tool result:\033[0m {tool_result}\n")

                self.history.append(
                    Message(
                        role="tool",
                        content=str(tool_result),
                        name=tc.name,
                        tool_call_id=tc.tool_call_id
                    )
                )

        # Hết max_steps mà vẫn chưa có câu trả lời → gọi model lần cuối
        messages = [Message(role="system", content=self.system_prompt), *self.history]
        response = self.model.chat(messages)
        self.history.append(Message(role="assistant", content=response.content))
        return response.content if response.content is not None else ""
