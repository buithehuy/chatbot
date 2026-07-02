import os
from dotenv import load_dotenv
from google import genai
from models.base import Model as BaseModel
from messages import Message

load_dotenv()



class GeminiModel(BaseModel):
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"

    def convert_messages(self, messages):
        content = []
        for msg in messages:
            role = msg.role
        
            if role == "assistant":
                role = "model"

            content.append({
                "role": role,
                "parts": [
                    {"text": msg.content}
                ]
            })
        return content


    def chat(self, messages):
        messages = self.convert_messages(messages)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=messages
        )
        answer = response.text
        return answer
    
