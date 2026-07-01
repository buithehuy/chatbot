from openai_model import OpenAIModel
from chatbot import ChatBot
from gemini_model import GeminiModel

openaimodel = OpenAIModel()
geminimodel = GeminiModel()

model = geminimodel

bot = ChatBot(model)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    answer = bot.chat(user_input)
    print("Bot:", answer)




