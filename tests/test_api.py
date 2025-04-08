import unittest
from unittest import mock

from fastapi.testclient import TestClient

from main import app
from src.core.doc_type import DocType
from src.core.validator import OperationException
from src.settings_manager import SettingsManager


class TestAPI(unittest.TestCase):

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

    # def test_rules_options(self):
    #     """Тест /api/rules/options"""
    #     response = self.client.get("/api/rules/options")
    #     self.assertEqual(response.status_code, 200, "Ошибка при запросе списка правил")
    #     self.assertTrue(response.json(), "Список правил пуст")

    def test_exact_rules(self):
        """Тест /api/rules/{doc_type}"""
        response = self.client.get("/api/rules/diploma")
        self.assertEqual(response.status_code, 200, "Ошибка при запросе правил для документа")
        self.assertTrue(response.json(), "Правила для документа не загружены")

    def test_change_rules(self):
        """Позитивный тест изменения правила с возвратом исходного значения"""
        doc_type = "diploma"
        rule_key = "common_rules.margins.top"
        new_value = "14"

        # Получение текущего значения
        original_rules = self.client.get(f"/api/rules/{doc_type}").json()
        original_value = original_rules
        for key in rule_key.split("."):
            original_value = original_value[key]

        try:
            # Изменение правила
            response = self.client.post("/api/rules/update", params={
                "doc_type": doc_type,
                "rule_key": rule_key,
                "new_value": new_value
            })
            self.assertEqual(response.status_code, 200, "Правило не удалось обновить")
            self.assertIn("успешно обновлено", response.json()["message"],
                          "Сообщение об успешном обновлении отсутствует")
        finally:
            # Возврат исходного значения
            self.client.post("/api/rules/update", params={
                "doc_type": doc_type,
                "rule_key": rule_key,
                "new_value": original_value
            })

    def test_change_rules_invalid_doc_type(self):
        """Тест /api/rules/update с неверным типом документа"""
        response = self.client.post("/api/rules/update", params={
            "doc_type": "unknown_type",
            "rule_key": "common_rules.margins.top",
            "new_value": "10"
        })
        self.assertEqual(response.status_code, 400, "Ожидалась ошибка 400 при неверном типе документа")
        self.assertIn("Неизвестный тип документа", response.json()["detail"])

    def test_change_rule_for_all(self):
        """Тест /api/rules/update/all с возвратом исходных значений"""
        rule_key = "common_rules.margins.top"
        new_value = "15"
        original_values = {}

        # Сохраняем все старые значения
        for doc_type in DocType:
            doc_name = doc_type.name.lower()
            rules = self.client.get(f"/api/rules/{doc_name}").json()
            original_value = rules
            for key in rule_key.split("."):
                original_value = original_value[key]
            original_values[doc_name] = original_value

        try:
            # Обновляем для всех
            response = self.client.post("/api/rules/update/all", params={
                "rule_key": rule_key,
                "new_value": new_value
            })
            self.assertEqual(response.status_code, 200, "Ошибка при обновлении правила для всех документов")
            self.assertIn("Правило common_rules.margins.top успешно обновлено для всех типов документов",
                          response.json()["message"])
            self.assertTrue(response.json()["updated"], "Список обновленных документов должен быть непустым")
        finally:
            # Возврат всех исходных значений
            for doc_name, old_value in original_values.items():
                self.client.post("/api/rules/update", params={
                    "doc_type": doc_name,
                    "rule_key": rule_key,
                    "new_value": old_value
                })

    def test_change_rule_for_all_with_error(self):
        """Тест /api/rules/update/all с ошибкой в одном из документов"""
        with mock.patch("src.logics.rule_service.RuleService.update_rule",
                        side_effect=lambda doc, key, value: (_ for _ in ()).throw(
                            OperationException("Ошибка")) if doc == DocType.DIPLOMA else None):
            response = self.client.post("/api/rules/update/all", params={
                "rule_key": "common_rules.margins.top",
                "new_value": "20"
            })
            self.assertEqual(response.status_code, 200, "Ошибка при обновлении правила для всех документов")
            self.assertIn("Некоторые обновления прошли с ошибками", response.json()["message"])
            self.assertTrue(response.json()["errors"], "Должны быть ошибки для одного из документов")

    def test_validate_document_single_file(self):
        pass

    def test_validate_document_latex(self):
        pass
