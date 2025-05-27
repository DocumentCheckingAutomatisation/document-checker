import unittest
from io import BytesIO
from pprint import pprint

from src.logics.checkers.latex_checker import LatexChecker
from src.logics.parsers.latex_parser import LatexParser
from src.settings_manager import SettingsManager


class TestLatexLogics(unittest.TestCase):
    def setUp(self):
        self.manager = SettingsManager()
        self.manager.open("../settings.json")

        with open("../docs/settings.sty", "rb") as f:
            self.reference_sty_content = f.read().decode("utf-8").splitlines()

    def test_parse_structure(self):
        with open("../docs/my.tex", "rb") as tex_file:
            parser = LatexParser(tex_file)
            pprint(parser.parsed_document["lists"])
            print()
            pprint(parser.errors)

        self.assertTrue(parser.parsed_document, "Структура документа не была распарсена")


    def test_check_sty_file(self):
        """Тест проверки соответствия загруженного .sty файла эталонному"""

        with open("../docs/my.tex", "rb") as tex_file, open("../docs/settings.sty", "rb") as sty_file:
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

    def test_latex_check_lists(self):
        pass

    def test_latex_check_regular_lists(self):
        with open("../docs/main.tex", "rb") as tex_file, open("../docs/settings.sty", "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, "course_work")
        checker.errors = []
        content = """
        Перечисление с русскими строчными буквами
        \\begin{enumasbuk}) 
        \\item Первый элемент 
        \\item второй элемент; 
        \\item третий элемент
        \\end{enumasbuk}
        """

        checker.check_regular_list(content)

        pprint(checker.errors)

    def test_latex_checking(self):
        """Тест проверки LaTeX-документа"""

        with open("../docs/my.tex", "rb") as tex_file, open("../docs/settings.sty", "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, "diploma")

        result = checker.check_document()
        # pprint(checker.parsed_document)
        print()
        pprint(checker.errors)


        self.assertTrue(result["valid"], "Структура документа не прошла проверку")


if __name__ == '__main__':
    unittest.main()
