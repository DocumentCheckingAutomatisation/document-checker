from abc import ABC, abstractmethod
import uuid

from src.core.validator import Validator


class AbstractModel(ABC):
    def __init__(self, name=None, id=None):
        self.name = name or ""
        self.id = id or str(uuid.uuid4())  # Уникальный идентификатор

    @abstractmethod
    def to_dict(self):
        """Метод для представления объекта в виде словаря"""
        pass

    def from_json(self, data: dict):
        self.id = data.get("id", str(uuid.uuid4()))
        self.name = data.get("name", "")

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self

    def __str__(self):
        return f"{self.name} ({self.id})"
