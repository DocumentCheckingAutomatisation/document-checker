import unittest

from src.logics.checkers.docx_checker import DocxChecker
from src.logics.parsers.docx_parser import DocxParser
from src.settings_manager import SettingsManager


class TestDocxLogics(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

    def test_docx_parse_structure(self):
        docx_file_path = "../docs/diploma_lib.docx"
        parser = DocxParser(docx_file_path)

        self.assertTrue(parser.parsed_document, "Структура документа не была распарсена")

    def test_docx_checking_with_mistakes(self):
        docx_file_path = "../docs/diploma_lib1.docx"
        checker = DocxChecker(docx_file_path, "diploma")

        result = checker.check_document()
        print("checker.errors", checker.errors)

        self.assertFalse(result["valid"], "Структура документа не прошла проверку")
        self.assertTrue(checker.errors,"Ошибки не были найдены")

