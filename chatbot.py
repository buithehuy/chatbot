from messages import Message

class ChatBot:
    def __init__(self, model):
        self.model = model
        self.history =[]
    def chat(self, user_input):
        self.history.append(Message(role="user", content=user_input))
        answer = self.model.chat(self.history)
        self.history.append(Message(role="assistant", content=answer))
        return answer
