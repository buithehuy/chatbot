from messages import Message

class ChatBot:
    def __init__(self, model):
        self.model = model
        self.system_prompt = "You  are an angry person"
        self.history =[]
    def chat(self, user_input):
        self.history.append(Message(role="user", content=user_input))
        messages = [Message(role="system", content=self.system_prompt), *self.history]
        answer = self.model.chat(messages)
        self.history.append(Message(role="assistant", content=answer))
        return answer
    