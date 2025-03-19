import unittest

from src.core.doc_type import DocType
from src.logics.rule_service import RuleService
from src.settings_manager import SettingsManager


class TestServices(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовой среды"""
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

    def test_rule_service_load_file(self):
        """Тест загрузки правил из файла"""
        rules = RuleService.load_rules(DocType.DIPLOMA)
        self.assertTrue(rules, "Ошибка при загрузке правил")
        self.assertTrue(rules["structure_rules"], "Ошибка при загрузке структурных правил")

    def test_rule_service_get_rule_types(self):
        """Тест получения типов правил"""
        types = RuleService.get_rule_types()
        self.assertTrue(types, "Ошибка при получении типов правил")