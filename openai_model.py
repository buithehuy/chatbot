from openai import OpenAI
from base_model import Model as BaseModel



class OpenAIModel(BaseModel):
    def __init__(self):
        self.client = OpenAI()

    def chat(self, messages):
        response = self.client.responses.create(
            model="gpt-5.5",
            input=messages
        )
        
        answer = response.output_text
        return answer