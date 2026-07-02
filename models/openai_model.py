import os
from dotenv import load_dotenv

from openai import OpenAI
from models.base import Model as BaseModel

load_dotenv()

class OpenAIModel(BaseModel):
    def __init__(self):
        self.client = OpenAI()

    def convert_messages(self, messages):
        content = []
        for msg in messages:
            role = msg.role
            content.append({
                "role": role,
                "content": msg.content
            })
        return content

    def chat(self, messages):
        messages = self.convert_messages(messages)
        response = self.client.responses.create(
            model="gpt-5.5",
            input=messages
        )
        
        answer = response.output_text
        return answer