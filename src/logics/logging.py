from datetime import datetime

from src.settings_manager import SettingsManager
from src.core.abstract_logic import AbstractLogic
from src.core.event_type import EventType
from src.core.logging_level import LoggingLevel
from src.core.validator import OperationException, Validator
from src.logics.observe_service import ObserveService


class Logging(AbstractLogic):
    __settings_manager: SettingsManager = None
    __log_file_path: str = "application.log"

    def __init__(self, manager: SettingsManager):
        Validator.validate(manager, SettingsManager)

        ObserveService.append(self)

        self.__settings_manager = manager
        self.current_logging_level = LoggingLevel(self.__settings_manager.current_settings.logging_level)

    def set_exception(self, ex: Exception):  # pragma: no cover
        super().set_exception(ex)

    def handle_event(self, event_type: EventType, params):
        super().handle_event(event_type, params)

        if event_type in {EventType.LOG_INFO, EventType.LOG_ERROR, EventType.LOG_DEBUG}:
            self._log_event(event_type, params)

    def _log_event(self, type: EventType, params):
        """
        Логирует событие, если оно соответствует текущему уровню логирования
        """
        if self._should_log(type):
            log_message = self._format_log_message(type, params)
            self._write_log(log_message)

    def _should_log(self, type: EventType) -> bool:
        """
        Определяет, нужно ли логировать событие на основе текущего уровня логирования
        """
        if self.current_logging_level == LoggingLevel.DEBUG:
            return type in {EventType.LOG_DEBUG, EventType.LOG_ERROR, EventType.LOG_INFO}
        elif self.current_logging_level == LoggingLevel.ERROR:
            return type in {EventType.LOG_ERROR, EventType.LOG_INFO}
        elif self.current_logging_level == LoggingLevel.INFO:
            return type == EventType.LOG_INFO
        return False

    @staticmethod
    def _format_log_message(type: EventType, params) -> str:
        """
        Форматирует сообщение для логирования
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{current_time} [{type.name}] {params}"

    def _write_log(self, message: str):
        """
        Записывает лог-сообщение в файл
        """
        try:
            with open(self.__log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(message + "\n")
        except Exception as ex:
            raise OperationException(f"Error writing to log file: {ex}")
        # print(message)
