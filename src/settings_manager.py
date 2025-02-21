import json
import os

from src.core.abstract_logic import AbstractLogic
from src.core.event_type import EventType
from src.core.logging_level import LoggingLevel
from src.core.validator import Validator
from src.logics.observe_service import ObserveService
from src.models.settings_model import SettingsModel


class SettingsManager(AbstractLogic):
    __file_name = "../settings.json"
    __settings: SettingsModel = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if self.__settings is None:
            self.__settings = self.__default_settings()

            ObserveService.append(self)

    def open(self, file_path: str = ""):
        if not isinstance(file_path, str):
            Validator.validate("file_path", "str")

        if file_path == "":
            file_path = os.path.join(os.curdir, self.__file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as stream:
                data = json.load(stream)
                self.convert(data)
            return True

        except Exception as ex:
            print(f"Ошибка загрузки: {ex}")
            self.__settings = self.__default_settings()
            self.set_exception(ex)
            return False

    def convert(self, data: dict):
        for key, value in data.items():
            if hasattr(self.__settings, key):
                setattr(self.__settings, key, value)

        # if self.__settings.report_settings is None:
        #     self.__settings.report_settings = {}

    @property
    def current_settings(self) -> SettingsModel:
        return self.__settings

    def __default_settings(self):
        data = SettingsModel()
        data.logging_level = LoggingLevel.DEBUG.value

        return data


    def save_settings(self):
        file_path = os.path.join(os.curdir, self.__file_name)

        settings_data = {
            "logging_level": self.__settings.logging_level.value
        }

        try:
            ObserveService.raise_event(EventType.LOG_INFO, params="Начало сохранения настроек в файл.")

            with open(file_path, 'w', encoding='utf-8') as stream:
                json.dump(settings_data, stream, ensure_ascii=False, indent=4)

            ObserveService.raise_event(EventType.LOG_INFO, params=f"Настройки успешно сохранены в файл: {file_path}")

        except Exception as ex:
            ObserveService.raise_event(EventType.LOG_ERROR, params=f"Ошибка при сохранении настроек: {str(ex)}")

            self.set_exception(ex)
            raise

    def set_exception(self, ex: Exception):
        self._inner_set_exception(ex)

    def handle_event(self, type: EventType, params):
        super().handle_event(type, params)

        # if type == EventType.CHANGE_BLOCK_PERIOD:
        #     self.save_settings()
        #
        # if type == EventType.SAVE_DATA:
        #     self.current_settings.first_start = False
        #     self.save_settings()