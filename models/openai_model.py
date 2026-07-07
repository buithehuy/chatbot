import os
from dotenv import load_dotenv

from openai import OpenAI
from models.base import Model as BaseModel
from responses import ChatResponse

load_dotenv()

class OpenAIModel(BaseModel):
    def __init__(self):
        self.client = OpenAI()

    def convert_messages(self, messages):
        contents = []
        system_prompt = None
        for msg in messages:
            role = msg.role
            if role == "system":
                system_prompt = msg.content
                continue
            contents.append({
                "role": role,
                "content": msg.content
            })
        return contents, system_prompt

    def chat(self, messages):
        messages = self.convert_messages(messages)
        response = self.client.responses.create(
            model="gpt-5.5",
            input=messages
        )
        
        return ChatResponse(
            content= response.output_text
        )