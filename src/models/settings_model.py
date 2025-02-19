from src.core.logging_level import LoggingLevel
from src.core.validator import Validator, ArgumentException


class SettingsModel:
    """Настройки"""
    __logging_level: LoggingLevel = LoggingLevel.DEBUG

    @property
    def logging_level(self):
        return self.__logging_level

    @logging_level.setter
    def logging_level(self, value: int):
        Validator.validate(value, int)
        try:
            self.__logging_level = LoggingLevel(value)
        except Exception:
            ArgumentException("logging_level - valid format integer (1-3)")
