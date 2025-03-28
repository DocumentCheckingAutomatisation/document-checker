import unittest

from src.logics.checkers.latex_checker import LatexChecker
from src.logics.parsers.latex_parser import LatexParser
from src.settings_manager import SettingsManager
from unittest.mock import MagicMock
from io import BytesIO


class TestLatexLogics(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

        with open("../docs/settings.sty", "rb") as f:
            self.reference_sty_content = f.read().decode("utf-8").splitlines()

    def test_parse_structure(self):
        with open("../docs/main.tex", "rb") as tex_file:
            parser = LatexParser(tex_file)
            print(parser.parsed_document)
            print()
            print(parser.errors)

        self.assertTrue(parser.parsed_document, "Структура документа не была распарсена")

    def test_latex_check_introduction_keywords(self):
        """Тест проверки ключевых слов во введении"""

        with open("../docs/main.tex", "rb") as tex_file:

            checker = LatexChecker(tex_file, None, "course_work")

        checker.check_introduction_keywords()
        print(checker.errors)

        self.assertTrue(not checker.errors, "Ключевые слова во введении не были")

    def test_check_sty_file(self):
        """Тест проверки соответствия загруженного .sty файла эталонному"""

        with open("../docs/main.tex", "rb") as tex_file, open("../docs/settings1.sty", "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, "course_work")

        checker.check_sty_file()

        self.assertFalse(checker.errors, "Ошибки не были найдены при несоответствии .sty файла")
        print(checker.errors)

    def test_check_wrong_sty_file(self):

        modified_sty_content = self.reference_sty_content[:]
        if modified_sty_content:
            modified_sty_content[0] = "Неверная строка"

        test_sty_file = BytesIO("\n".join(modified_sty_content).encode("utf-8"))

        with open("../docs/main.tex", "rb") as tex_file:
            checker = LatexChecker(tex_file, test_sty_file, "course_work")

        checker.check_sty_file()

        self.assertTrue(checker.errors, "Ошибки не были найдены при несоответствии .sty файла")
        print(checker.errors)

    def test_latex_checking(self):
        """Тест проверки LaTeX-документа"""

        with open("../docs/main.tex", "rb") as tex_file, open("../docs/settings.sty", "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, "course_work")

        result = checker.check_document()
        print(checker.parsed_document)
        print()
        print(checker.errors)

        self.assertTrue(result["valid"], "Структура документа не прошла проверку")


if __name__ == '__main__':
    unittest.main()
