from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GEMINI_MODEL_NAME = "gemini-2.5-flash"

    GROQ_MODEL_NAME = "llama-3.3-70b-versatile"

    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


    SYSTEM_PROMPT = """
    You are a helpful assistant.

    User's city: Hanoi
    Country: Vietnam
    """