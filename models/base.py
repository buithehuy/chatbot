from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def convert_messages(self, messages):
        pass
    
    @abstractmethod
    def chat(self, messages):
        pass
   