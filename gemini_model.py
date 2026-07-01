from google import genai
from base_model import Model as BaseModel

class GeminiModel(BaseModel):
    def __init__(self):
        self.client = genai.Client()

    def chat(self, messages):
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages
        )
        answer = response.text
        return answer