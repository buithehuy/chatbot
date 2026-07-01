from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def chat(self, messages):
        pass