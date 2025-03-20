import unittest

from fastapi.testclient import TestClient

from main import app
from src.logics.checkers.latex_checker import LatexChecker
from src.settings_manager import SettingsManager


class TestLogics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Настройка тестового клиента"""
        cls.client = TestClient(app)
        cls.manager = SettingsManager()
        cls.manager.open("../settings.json")

    def test_docs_options(self):
        """Тест /api/documents/options"""
        response = self.client.get("/api/documents/options")
        self.assertEqual(response.status_code, 200, "Ошибка при запросе списка документов")
        self.assertTrue(response.json(), "Список документов пуст")

    def test_rules_options(self):
        """Тест /api/rules/options"""
        response = self.client.get("/api/rules/options")
        self.assertEqual(response.status_code, 200, "Ошибка при запросе списка правил")
        self.assertTrue(response.json(), "Список правил пуст")

    def test_exact_rules(self):
        """Тест /api/rules/{doc_type}"""
        response = self.client.get("/api/rules/diploma")
        self.assertEqual(response.status_code, 200, "Ошибка при запросе правил для документа")
        self.assertTrue(response.json(), "Правила для документа не загружены")

    def test_change_rules(self):
        pass

    def test_validate_document_single_file(self):
        pass

    def test_validate_document_latex(self):
        pass


