from tools.base import BaseTool
import requests



class Weather(BaseTool):

    def __init__(self, api_key):
        self.api_key = api_key

    @property
    def name(self):
        return "weather"

    @property
    def description(self):
        return "Check the weather"

    def execute(self, city):
        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        return response.json()

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Name of a city like Hanoi, Tokyo"
                        }
                    },
                    "required": ["city"]
                }
            }
        }