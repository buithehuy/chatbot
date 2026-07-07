from abc import ABC, abstractmethod
from responses import ChatResponse

class Model(ABC):
    @abstractmethod
    def convert_messages(self, messages):
        pass

    @abstractmethod
    def chat(self, messages) -> ChatResponse:
        pass
        
    def set_tools(self, tools):
        self.tools = tools
        