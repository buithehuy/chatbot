from google import genai
from models.base import Model as BaseModel
from google import genai
from google.genai import types
from responses import ChatResponse

from config import Settings



class GeminiModel(BaseModel):
    def __init__(self):
        self.client = genai.Client()
        self.model_name = Settings.GEMINI_MODEL_NAME

    def convert_messages(self, messages):
        contents = []
        system_prompt = None
        for msg in messages:
            role = msg.role

            if role == "system":
                system_prompt = msg.content
                continue
        
            if role == "assistant":
                role = "model"

            contents.append({
                "role": role,
                "parts": [
                    {"text": msg.content}
                ]
            })
        return contents, system_prompt


    def chat(self, messages):
        contents, system_prompt= self.convert_messages(messages)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        
        return ChatResponse(
            content=response.text
        )
    