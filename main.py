from models.openai_model import OpenAIModel
from chatbot import ChatBot
from models.gemini_model import GeminiModel
from models.groq_model import GroqModel
from tools.tool_executor import ToolExecutor
from tools.tool_registry import ToolRegistry
from tools.calculator import CalculatorTool
from tools.weather import Weather
from config import Settings

api_key = Settings.OPENWEATHER_API_KEY

openaimodel = OpenAIModel()
geminimodel = GeminiModel()
groqmodel = GroqModel()

registry = ToolRegistry()
registry.register(CalculatorTool())
registry.register(Weather(api_key))

executor = ToolExecutor(registry)

# model = geminimodel
# model = openaimodel
model = groqmodel


# Temporarily disable tools to test basic chat
bot = ChatBot(model, tool_executor=executor)

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    answer = bot.chat(user_input)
    print("Bot:", answer)




