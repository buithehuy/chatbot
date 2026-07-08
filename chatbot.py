from messages import Message, AssistantMessage
from tools.tool_executor import ToolExecutor
from config import Settings

class ChatBot:
    def __init__(self, model, tool_executor=None, retriever=None):
        self.model = model
        self.tool_executor = tool_executor
        self.retriever = retriever
        self.base_system_prompt = Settings.SYSTEM_PROMPT
        self.history =[]

        if tool_executor:
            tools_list = [tool_executor.registry.tools[name] for name in tool_executor.registry.tools]
            self.model.set_tools(tools_list)

    def chat(self, user_input):
        self.history.append(Message(role="user", content=user_input))
        current_system_prompt = self.base_system_prompt

        if self.retriever:
                    # Tìm top 3 đoạn liên quan nhất dựa trên câu hỏi mới nhất của user
                    context_chunks = self.retriever.retrieve(user_input, top_k=3)
                    
                    if context_chunks:
                        # Gộp các đoạn text lại thành một khối tài liệu tham khảo
                        context_str = "\n---\n".join(context_chunks)
                        
                        # Cập nhật System Prompt tạm thời cho lượt chat này, ép mô hình trả lời dựa theo tài liệu
                        current_system_prompt = (
                            f"{self.base_system_prompt}\n\n"
                            f"Sử dụng thông tin ngữ cảnh (Context) sau đây để trả lời câu hỏi của người dùng. "
                            f"Nếu thông tin không có trong ngữ cảnh, hãy tự dựa vào kiến thức của bạn hoặc báo không có thông tin rõ ràng.\n"
                            f"=== CONTEXT ===\n{context_str}\n==============="
                        )


        messages = [Message(role="system", content=current_system_prompt), *self.history]
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
            messages = [Message(role="system", content=current_system_prompt), *self.history]
            response = self.model.chat(messages)

            self.history.append(
                Message(
                    role="assistant",
                    content=response.content
                )
            )

        return response.content if response.content is not None else ""
