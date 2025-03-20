import unittest

from src.logics.checkers.latex_checker import LatexChecker
from src.logics.parsers.latex_parser import LatexParser
from src.settings_manager import SettingsManager


class TestCheckingLatex(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

    def test_parse_structure(self):
        with open("../docs/main.tex", "rb") as tex_file:
            parser = LatexParser(tex_file)
            print(parser.structure)

        self.assertTrue(parser.structure, "Структура документа не была распарсена")

    def test_latex_checking(self):
        """Тест проверки LaTeX-документа"""

        with open("../docs/main.tex", "rb") as tex_file, open("../docs/settings.sty", "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, "diploma")

        result = checker.check_document()
        print(checker.parsed_structure)
        print(checker.errors)

        self.assertTrue(result["valid"], "Структура документа не прошла проверку")


if __name__ == '__main__':
    unittest.main()
