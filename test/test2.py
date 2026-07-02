from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

stream = client.interactions.create(
    model="gemini-2.5-flash",
    input="Count to from 1 to 25.",
    stream=True,
)
for event in stream:
    if event.event_type == "step.delta":
        if event.delta.type == "text":
            print(event.delta.text, end="", flush=True)