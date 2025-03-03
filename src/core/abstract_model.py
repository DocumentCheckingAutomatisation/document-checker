import uuid
from abc import ABC, abstractmethod

from src.core.validator import Validator


class AbstractModel(ABC):
    __id: str = ""
    __name: str = ""

    def __init__(self):
        self.__id: str = str(uuid.uuid4())  # Уникальный идентификатор

    @property
    def id(self) -> str:
        """Уникальный идентификатор"""
        return self.__id

    @property
    def name(self) -> str:
        """Наименование"""
        return self.__name

    @name.setter
    def name(self, value: str):
        """Наименование"""
        Validator.validate(value, str, 255)
        self.__name = value.strip()

    @abstractmethod
    def to_dict(self):
        """Метод для представления объекта в виде словаря"""
        pass

    @abstractmethod
    def from_dict(self, data: dict):
        """Метод для создания объекта из словаря"""
        self.name = data.get("name", "")

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self

    def __str__(self):
        return f"{self.name} ({self.id})"
