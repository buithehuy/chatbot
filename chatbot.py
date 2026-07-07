from messages import Message, AssistantMessage
from tools.tool_executor import ToolExecutor

class ChatBot:
    def __init__(self, model, tool_executor=None):
        self.model = model
        self.tool_executor = tool_executor
        self.system_prompt = "Your name is Bob"
        self.history =[]

        if tool_executor:
            tools_list = [tool_executor.registry.tools[name] for name in tool_executor.registry.tools]
            self.model.set_tools(tools_list)

    def chat(self, user_input):
        self.history.append(Message(role="user", content=user_input))
        messages = [Message(role="system", content=self.system_prompt), *self.history]
        response = self.model.chat(messages)
        if response.tool_call is None:
            self.history.append(Message(role="assistant", content=response.content))
        else:
            tc = response.tool_call
            print(f"\n\033[93m⚙ Tool call:\033[0m \033[96m{tc.name}\033[0m  args={tc.arguments}")
            tool_result = self.tool_executor.execute(tc)
            print(f"\033[93m⚙ Tool result:\033[0m {tool_result}\n")
            # Lưu assistant message kèm raw_tool_calls để Groq nhận đúng
            self.history.append(
                AssistantMessage(
                    content=None,
                    raw_tool_calls=response.raw_tool_calls
                )
            )
            self.history.append(
                Message(
                    role="tool",
                    content=str(tool_result),
                    name=response.tool_call.name,
                    tool_call_id=response.tool_call.tool_call_id
                )
            )
            messages = [Message(role="system", content=self.system_prompt), *self.history]
            response = self.model.chat(messages)

            self.history.append(
                Message(
                    role="assistant",
                    content=response.content
                )
            )

        return response.content if response.content is not None else ""
