import json
import os
import unittest
from src.core.validator import ArgumentException
from src.core.logging_level import LoggingLevel
from src.models.settings_model import SettingsModel
from src.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):

    def test_load_settings(self):
        manager = SettingsManager()
        result = manager.open("../settings.json")
        print(result)
        self.assertTrue(result)
        self.assertEqual(manager.current_settings.logging_level, LoggingLevel(3))

    def test_settings_manager_open_fail(self):
        manager1 = SettingsManager()

        manager1.open("../settings58.json")

        print(manager1.error_text)
        self.assertTrue(manager1.is_error)

    def test_default_settings(self):
        manager = SettingsManager()
        result = manager.open("nonexistent_settings.json")

        self.assertFalse(result)
        self.assertEqual(manager.current_settings.logging_level, LoggingLevel.DEBUG)

    def test_singleton(self):
        manager1 = SettingsManager()
        manager1.open("../settings.json")

        manager2 = SettingsManager()

        self.assertEqual(manager2.current_settings.logging_level, manager1.current_settings.logging_level)
        self.assertIs(manager1, manager2)

    def test_open_invalid_type(self):
        # Передача некорректного типа в file_path
        manager = SettingsManager()

        with self.assertRaises(ArgumentException) as context:
            manager.open(123)
        print(str(context.exception))
        self.assertTrue("Передан некорректный тип для проверки." in str(context.exception))

    def test_logging_level_type_getter(self):
        settings_instance = SettingsModel()
        expected_value = 3
        settings_instance._settings__logging_level = expected_value

        self.assertEqual(settings_instance.logging_level, LoggingLevel(expected_value))

    def test_logging_level_type_setter(self):
        settings_instance = SettingsModel()
        valid_value = 1
        settings_instance.logging_level = valid_value
        self.assertEqual(settings_instance.logging_level, LoggingLevel(valid_value))


class TestSavingSettingsManager(unittest.TestCase):

    def setUp(self):
        # Подготовка к тесту
        self.manager = SettingsManager()
        self.file_path = os.path.join(os.curdir, "../settings.json")

    def test_save_settings(self):
        self.manager.current_settings.logging_level = 2

        self.manager.save_settings()

        self.assertTrue(os.path.exists(self.file_path), "Файл настроек не был создан.")

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertEqual(data["logging_level"], 2)

        self.manager.current_settings.logging_level = 3
        self.manager.save_settings()


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
