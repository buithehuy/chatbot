class ChatBot:
    def __init__(self, model):
        self.model = model
        self.history =[]
    def chat(self, user_input):
        # self.history.append({"role": "user", "content": user_input})
        self.history.append(
            {"role": "user",
             "parts":[
                 {"text": user_input}
             ]}
        )
        answer = self.model.chat(self.history)
        # self.history.append({"role": "assistant", "content": answer})
        self.history.append(
            {"role": "model",
             "parts":[
                 {"text": answer}
             ]}
        )
        return answer
