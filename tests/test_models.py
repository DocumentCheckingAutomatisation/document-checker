import unittest

from src.core.doc_type import DocType
from src.core.rule_type import RuleType
from src.models.document import Document
from src.models.mistake import Mistake
from src.models.recommendation import Recommendation
from src.models.rule import Rule
from src.models.validation_result import ValidationResult
from src.models.validation_rules import ValidationRules
from src.settings_manager import SettingsManager


class TestModels(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовой среды"""
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

    def test_document_creation(self):
        document = Document()
        document.name = "Документ 1"
        document.doc_type = DocType(1)
        document.result = ValidationResult()

        self.assertIsNotNone(document.id)
        self.assertEqual(document.name, "Документ 1")
        self.assertEqual(document.doc_type, DocType.DIPLOMA)
        self.assertIsInstance(document.result, ValidationResult)

    def test_document_to_dict(self):
        """Тест конвертации в словарь"""
        document = Document()
        document.name = "Тестовый документ"
        document.doc_type = DocType.DIPLOMA
        document.result = ValidationResult()

        doc_dict = document.to_dict()
        self.assertEqual(doc_dict["name"], "Тестовый документ")
        self.assertEqual(doc_dict["doc_type"], "DIPLOMA")
        self.assertIsInstance(doc_dict["result"], dict)

    def test_document_from_dict(self):
        """Тест восстановления документа из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовый документ",
            "doc_type": "DIPLOMA",
            "result": {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Тест результат', 'mistakes': [],
                       'recommendations': []}
        }
        document = Document()
        document.from_dict(data)
        self.assertEqual(document.name, "Тестовый документ")
        self.assertEqual(document.doc_type, DocType.DIPLOMA)
        self.assertIsInstance(document.result, ValidationResult)
        self.assertEqual(document.result.name, "Тест результат")

    def test_document_equality(self):
        """Тест сравнения двух документов"""
        doc1 = Document()
        doc1.name = "Документ"
        doc1.doc_type = DocType.COURSE_WORK
        doc1.result = ValidationResult()

        doc2 = Document()
        doc2.name = "Документ"
        doc2.doc_type = DocType.COURSE_WORK
        doc2.result = ValidationResult()

        self.assertEqual(doc1, doc2)

    def test_document_string_representation(self):
        """Тест строкового представления документа"""
        document = Document()
        document.name = "Документ"
        document.doc_type = DocType.PRACTICE_REPORT
        document.result = ValidationResult()

        doc_str = str(document)
        self.assertIn("Документ", doc_str)
        self.assertIn("PRACTICE_REPORT", doc_str)

    def test_mistake_creation(self):
        mistake = Mistake()
        mistake.name = "Ошибка 1"
        mistake.rule = Rule()
        mistake.message = "Сообщение об ошибке"

        self.assertIsNotNone(mistake.id)
        self.assertEqual(mistake.name, "Ошибка 1")
        self.assertIsNotNone(mistake.rule)
        self.assertEqual(mistake.message, "Сообщение об ошибке")

    def test_mistake_to_dict(self):
        """Тест конвертации в словарь"""
        mistake = Mistake()
        mistake.name = "Тестовая ошибка"
        mistake.rule = Rule()
        mistake.message = "Сообщение об ошибке"

        mistake_dict = mistake.to_dict()
        self.assertEqual(mistake_dict["name"], "Тестовая ошибка")
        self.assertIsInstance(mistake_dict["rule"], dict)
        self.assertEqual(mistake_dict["message"], "Сообщение об ошибке")

    def test_mistake_from_dict(self):
        """Тест восстановления ошибки из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовая ошибка",
            "rule": {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Правило 1', 'attribute': 'Атрибут 1',
                     'rule_type': 'COMMON', 'condition': 'Условие 1'},
            "message": "Сообщение об ошибке"
        }
        mistake = Mistake()
        mistake.from_dict(data)

        self.assertEqual(mistake.name, "Тестовая ошибка")
        self.assertIsInstance(mistake.rule, Rule)
        self.assertEqual(mistake.message, "Сообщение об ошибке")

    def test_mistake_equality(self):
        """Тест сравнения двух ошибок"""
        mistake1 = Mistake()
        mistake1.name = "Ошибка"
        mistake1.rule = Rule()
        mistake1.message = "Сообщение"

        mistake2 = Mistake()
        mistake2.name = "Ошибка"
        mistake2.rule = Rule()
        mistake2.message = "Сообщение"

        self.assertEqual(mistake1, mistake2)

    def test_mistake_string_representation(self):
        """Тест строкового представления ошибки"""
        mistake = Mistake()
        mistake.name = "Ошибка"
        mistake.rule = Rule()
        mistake.message = "Сообщение"

        mistake_str = str(mistake)
        self.assertIn("Ошибка", mistake_str)
        self.assertIn("Сообщение", mistake_str)

    def test_recommendation_creation(self):
        recom = Recommendation()
        recom.name = "Рекомендация 1"
        recom.mistake = Mistake()
        recom.message = "Сообщение c рекомендацией"

        self.assertIsNotNone(recom.id)
        self.assertEqual(recom.name, "Рекомендация 1")
        self.assertIsNotNone(recom.mistake)
        self.assertEqual(recom.message, "Сообщение c рекомендацией")

    def test_recommendation_to_dict(self):
        """Тест конвертации в словарь"""
        recom = Recommendation()
        recom.name = "Тестовая рекомендация"
        recom.mistake = Mistake()
        recom.mistake.rule = Rule()
        recom.message = "Сообщение c рекомендацией"

        recom_dict = recom.to_dict()
        self.assertEqual(recom_dict["name"], "Тестовая рекомендация")
        self.assertIsInstance(recom_dict["mistake"], dict)
        self.assertEqual(recom_dict["message"], "Сообщение c рекомендацией")

    def test_recommendation_from_dict(self):
        """Тест восстановления рекомендации из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовая рекомендация",
            "mistake": {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Ошибка 1',
                        'rule': {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Правило 1',
                                 'attribute': 'Атрибут 1', 'rule_type': 'COMMON', 'condition': 'Условие 1'},
                        'message': 'Сообщение об ошибке'},
            "message": "Сообщение c рекомендацией"
        }
        recom = Recommendation()
        recom.from_dict(data)

        self.assertEqual(recom.name, "Тестовая рекомендация")
        self.assertIsInstance(recom.mistake, Mistake)
        self.assertEqual(recom.message, "Сообщение c рекомендацией")

    def test_recommendation_equality(self):
        """Тест сравнения двух рекомендаций"""
        recom1 = Recommendation()
        recom1.name = "Рекомендация"
        recom1.mistake = Mistake()
        recom1.message = "Сообщение"

        recom2 = Recommendation()
        recom2.name = "Рекомендация"
        recom2.mistake = Mistake()
        recom2.message = "Сообщение"

        self.assertEqual(recom1, recom2)

    def test_recommendation_string_representation(self):
        """Тест строкового представления рекомендации"""
        recom = Recommendation()
        recom.name = "Рекомендация"
        recom.mistake = Mistake()
        recom.message = "Сообщение"

        recom_str = str(recom)
        self.assertIn("Рекомендация", recom_str)
        self.assertIn("Сообщение", recom_str)

    def test_rule_creation(self):
        rule = Rule()
        rule.name = "Правило 1"
        rule.attribute = "Атрибут 1"
        rule.rule_type = RuleType(1)
        rule.condition = "Условие 1"

        self.assertIsNotNone(rule.id)
        self.assertEqual(rule.name, "Правило 1")
        self.assertEqual(rule.rule_type, RuleType.COMMON)
        self.assertEqual(rule.condition, "Условие 1")

    def test_rule_to_dict(self):
        """Тест конвертации в словарь"""
        rule = Rule()
        rule.name = "Тестовое правило"
        rule.attribute = "Атрибут 1"
        rule.rule_type = RuleType.COMMON
        rule.condition = "Условие 1"

        rule_dict = rule.to_dict()
        self.assertEqual(rule_dict["name"], "Тестовое правило")
        self.assertEqual(rule_dict["attribute"], "Атрибут 1")
        self.assertEqual(rule_dict["rule_type"], "COMMON")
        self.assertEqual(rule_dict["condition"], "Условие 1")

    def test_rule_from_dict(self):
        """Тест восстановления правила из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовое правило",
            "attribute": "Атрибут 1",
            "rule_type": "COMMON",
            "condition": "Условие 1"
        }
        rule = Rule()
        rule.from_dict(data)

        self.assertEqual(rule.name, "Тестовое правило")
        self.assertEqual(rule.attribute, "Атрибут 1")
        self.assertEqual(rule.rule_type, RuleType.COMMON)
        self.assertEqual(rule.condition, "Условие 1")

    def test_rule_equality(self):
        """Тест сравнения двух правил"""
        rule1 = Rule()
        rule1.name = "Правило"
        rule1.attribute = "Атрибут 1"
        rule1.rule_type = RuleType.COMMON
        rule1.condition = "Условие 1"

        rule2 = Rule()
        rule2.name = "Правило"
        rule2.attribute = "Атрибут 1"
        rule2.rule_type = RuleType.COMMON
        rule2.condition = "Условие 1"

        self.assertEqual(rule1, rule2)

    def test_rule_string_representation(self):
        """Тест строкового представления правила"""
        rule = Rule()
        rule.name = "Правило"
        rule.attribute = "Атрибут 1"
        rule.rule_type = RuleType.COMMON
        rule.condition = "Условие 1"

        rule_str = str(rule)
        self.assertIn("Правило", rule_str)
        self.assertIn("Атрибут 1", rule_str)
        self.assertIn("Условие 1", rule_str)

    def test_validation_result_creation(self):
        val_result = ValidationResult()
        val_result.name = "Результат проверки 1"
        val_result.recommendations = [Recommendation()]
        val_result.mistakes = [Mistake()]

        self.assertIsNotNone(val_result.id)
        self.assertEqual(val_result.name, "Результат проверки 1")
        self.assertEqual(val_result.recommendations, [Recommendation()])
        self.assertEqual(val_result.mistakes, [Mistake()])

    def test_validation_result_to_dict(self):
        """Тест конвертации в словарь"""
        val_result = ValidationResult()
        val_result.name = "Тестовый результат"

        mstk = Mistake()
        mstk.rule = Rule()

        val_result.mistakes = [mstk]
        val_result.recommendations = [Recommendation()]
        val_result.recommendations[0].mistake = mstk

        result_dict = val_result.to_dict()
        self.assertEqual(result_dict["name"], "Тестовый результат")
        self.assertIsInstance(result_dict["recommendations"], list)
        self.assertIsInstance(result_dict["mistakes"], list)

    def test_validation_result_from_dict(self):
        """Тест восстановления результата проверки из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовый результат",
            "recommendations": [{'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Рекомендация 1',
                                 'mistake': {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Ошибка 1',
                                             'rule': {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Правило 1',
                                                      'attribute': 'Атрибут 1', 'rule_type': 'COMMON',
                                                      'condition': 'Условие 1'}, 'message': 'Сообщение об ошибке'},
                                 'message': 'Сообщение c рекомендацией'}],
            "mistakes": [{'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Ошибка 1',
                          'rule': {'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Правило 1',
                                   'attribute': 'Атрибут 1', 'rule_type': 'COMMON', 'condition': 'Условие 1'},
                          'message': 'Сообщение об ошибке'}]
        }
        val_result = ValidationResult()
        val_result.from_dict(data)

        self.assertEqual(val_result.name, "Тестовый результат")
        self.assertIsInstance(val_result.recommendations, list)
        self.assertIsInstance(val_result.mistakes, list)

    def test_validation_result_equality(self):
        """Тест сравнения двух результатов проверки"""
        val_result1 = ValidationResult()
        val_result1.name = "Результат проверки"
        val_result1.recommendations = [Recommendation()]
        val_result1.mistakes = [Mistake()]

        val_result2 = ValidationResult()
        val_result2.name = "Результат проверки"
        val_result2.recommendations = [Recommendation()]
        val_result2.mistakes = [Mistake()]

        self.assertEqual(val_result1, val_result2)

    def test_validation_result_string_representation(self):
        """Тест строкового представления результата проверки"""
        val_result = ValidationResult()
        val_result.name = "Результат проверки"
        val_result.recommendations = [Recommendation()]
        val_result.mistakes = [Mistake()]

        result_str = str(val_result)
        self.assertIn("Результат проверки", result_str)

    def test_validation_rules_creation(self):
        val_rules = ValidationRules()
        val_rules.name = "Правила проверки 1"
        val_rules.rules = [Rule()]
        val_rules.doc_type = DocType(1)

        self.assertIsNotNone(val_rules.id)
        self.assertEqual(val_rules.name, "Правила проверки 1")
        self.assertEqual(val_rules.rules, [Rule()])
        self.assertEqual(val_rules.doc_type, DocType.DIPLOMA)

    def test_validation_rules_to_dict(self):
        """Тест конвертации в словарь"""
        val_rules = ValidationRules()
        val_rules.name = "Тестовые правила проверки"
        val_rules.rules = [Rule()]
        val_rules.doc_type = DocType.DIPLOMA

        rules_dict = val_rules.to_dict()
        self.assertEqual(rules_dict["name"], "Тестовые правила проверки")
        self.assertIsInstance(rules_dict["rules"], list)
        self.assertEqual(rules_dict["doc_type"], "DIPLOMA")

    def test_validation_rules_from_dict(self):
        """Тест восстановления правил проверки из словаря"""
        data = {
            "id": "03aa2b0e-7cf9-44f6-93b4-80ead19cffc8",
            "name": "Тестовые правила проверки",
            "rules": [{'id': '5fdd6505-be16-48e9-bea5-2c07a06e5e2d', 'name': 'Правило 1', 'attribute': 'Атрибут 1',
                       'rule_type': 'COMMON', 'condition': 'Условие 1'}],
            "doc_type": "DIPLOMA"
        }
        val_rules = ValidationRules()
        val_rules.from_dict(data)

        self.assertEqual(val_rules.name, "Тестовые правила проверки")
        self.assertIsInstance(val_rules.rules, list)
        self.assertEqual(val_rules.doc_type, DocType.DIPLOMA)

    def test_validation_rules_equality(self):
        """Тест сравнения двух правил проверки"""
        val_rules1 = ValidationRules()
        val_rules1.name = "Правила проверки"
        val_rules1.rules = [Rule()]
        val_rules1.doc_type = DocType.DIPLOMA

        val_rules2 = ValidationRules()
        val_rules2.name = "Правила проверки"
        val_rules2.rules = [Rule()]
        val_rules2.doc_type = DocType.DIPLOMA

        self.assertEqual(val_rules1, val_rules2)

    def test_validation_rules_string_representation(self):
        """Тест строкового представления правил проверки"""
        val_rules = ValidationRules()
        val_rules.name = "Правила проверки"
        val_rules.rules = [Rule()]
        val_rules.doc_type = DocType.DIPLOMA

        rules_str = str(val_rules)
        self.assertIn("Правила проверки", rules_str)
        self.assertIn("DIPLOMA", rules_str)
