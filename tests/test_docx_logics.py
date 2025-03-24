import unittest

from src.logics.checkers.docx_checker import DocxChecker
from src.logics.parsers.docx_parser import DocxParser
from src.settings_manager import SettingsManager


class TestDocxLogics(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

    def test_parse_structure(self):
        with open("../docs/main.docx", "rb") as docx_file:
            parser = DocxParser(docx_file)
            print(parser.parsed_document)

        self.assertTrue(parser.parsed_document, "Структура документа не была распарсена")