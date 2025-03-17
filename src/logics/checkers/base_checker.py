from abc import ABC, abstractmethod

class BaseChecker(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def check_structure(self):
        pass

    @abstractmethod
    def check_formatting(self):
        pass

    def validate(self):
        """Общий метод, вызывающий все проверки"""
        return {
            "structure_errors": self.check_structure(),
            "formatting_errors": self.check_formatting()
        }
