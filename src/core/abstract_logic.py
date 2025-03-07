from abc import ABC, abstractmethod

from src.core.event_type import EventType
from src.core.validator import Validator


class AbstractLogic(ABC):
    """Абстрактный класс для обработки логики"""
    __error_text: str = ""

    @property
    def error_text(self) -> str:
        return self.__error_text.strip()

    @error_text.setter
    def error_text(self, message: str):
        Validator.validate(message, str)
        self.__error_text = message.strip()

    @property
    def is_error(self) -> bool:
        return self.error_text != ""

    def _inner_set_exception(self, ex: Exception):
        self.__error_text = f"Ошибка! Исключение {ex}"

    @abstractmethod
    def set_exception(self, ex: Exception):  # pragma: no cover
        """Абстрактный метод для загрузки и обработки исключений"""
        pass

    @abstractmethod
    def handle_event(self, event_type: EventType, params):
        """Обработка"""
        Validator.validate(event_type, EventType)
