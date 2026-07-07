from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

stream = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Write a 200-word fantasy novel."
)

for chunk in stream:
    if chunk.text:
        print(chunk.text, end="", flush=True)