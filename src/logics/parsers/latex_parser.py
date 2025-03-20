import re
from typing import Dict, Any


class LatexParser:
    def __init__(self, tex_file):
        self.tex_content = tex_file.read().decode("utf-8")
        self.errors = []
        self.structure = self.parse_structure()
        self.run_checks()

    def parse_structure(self) -> Dict[str, Any]:
        # Найдем все нумерованные главы
        numbered_chapters = re.findall(r'\\chapter\{(.+?)\}', self.tex_content)
        numbered_chapters_formatted = [f"{i+1} глава" for i in range(len(numbered_chapters))]

        # Найдем все нумерованные разделы
        sections = re.findall(r'\\section\{(.+?)\}', self.tex_content)

        # Сформируем список с номерами разделов, например "1.1 Название раздела"
        numbered_sections = []
        chapter_counter = 0
        section_counter = 0

        for section in sections:
            # При переходе к новой главе сбрасываем счетчик разделов
            if section_counter == 0 or (section_counter == 1 and section not in sections[:sections.index(section)]):
                chapter_counter += 1
                section_counter = 1  # сбрасываем счетчик секций для каждой новой главы
            else:
                section_counter += 1

            numbered_sections.append(f"{chapter_counter}.{section_counter} {section}")

        return {
            "numbered_chapters": numbered_chapters_formatted,
            "unnumbered_chapters": re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content),
            "numbered_sections": numbered_sections,
            "unnumbered_sections": re.findall(r'\\section\*\{(.+?)\}', self.tex_content),
        }

    def run_checks(self):
        self.parse_title_and_toc()
        self.parse_addcontentsline()

    def parse_title_and_toc(self):
        title_pattern = r"\\includepdf.*\{.*?\}"
        toc_pattern = r"\\tableofcontents"
        begin_doc_pattern = r"\\begin\{document\}"

        begin_match = re.search(begin_doc_pattern, self.tex_content)
        title_match = re.search(title_pattern, self.tex_content)
        toc_match = re.search(toc_pattern, self.tex_content)

        # Добавляем титульный лист в структуру, если найден
        if title_match:
            self.structure["unnumbered_chapters"].append("титульный лист")
        else:
            self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")

        # Добавляем содержание в структуру, если найдено
        if toc_match:
            self.structure["unnumbered_chapters"].append("содержание")
        else:
            self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")

        # Проверяем порядок следования команд
        if title_match and begin_match and title_match.start() < begin_match.start():
            self.errors.append("Ошибка: титульный лист должен подключаться после \\begin{document}.")
        if title_match and toc_match:
            between_text = self.tex_content[title_match.end():toc_match.start()]
            allowed_text = re.sub(r'%.+?\n', '', between_text).strip()
            if allowed_text and allowed_text != "\\setcounter{page}{2}":
                self.errors.append(
                    "Ошибка: между \\includepdf и \\tableofcontents допускаются только комментарии или \\setcounter{page}{2}.")

    def parse_addcontentsline(self):
        chapter_star_pattern = re.finditer(r"\\chapter\*\{(.+?)\}", self.tex_content)
        addcontents_pattern = r"\\addcontentsline\{toc\}\{chapter\}\{(.+?)\}"

        for match in chapter_star_pattern:
            start_pos = match.end()
            following_text = self.tex_content[start_pos:]
            add_match = re.search(addcontents_pattern, following_text)
            if not add_match or add_match.start() > 100:
                self.errors.append(
                    f"Ошибка: после \\chapter*{{{match.group(1)}}} отсутствует соответствующая команда \\addcontentsline."
                )

    def parse_counters(self):
        pass

    def parse_inroduction(self):
        pass  # better in checking file

    def parse_refs(self):
        pass  # better in checking file




# import re
# from typing import Dict, Any
#
#
# class LatexParser:
#     def __init__(self, tex_file):
#         self.tex_content = tex_file.read().decode("utf-8")
#         self.errors = []
#         self.structure = self.parse_structure()
#         self.run_checks()
#
#     def parse_structure(self) -> Dict[str, Any]:
#         return {
#             "numbered_chapters": re.findall(r'\\chapter\{(.+?)\}', self.tex_content),
#             "unnumbered_chapters": re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content),
#             "numbered_sections": re.findall(r'\\section\{(.+?)\}', self.tex_content),
#             "unnumbered_sections": re.findall(r'\\section\*\{(.+?)\}', self.tex_content),
#         }
#
#     def run_checks(self):
#         self.parse_title_and_toc()
#         self.parse_addcontentsline()
#
#     def parse_title_and_toc(self):
#         title_pattern = r"\\includepdf.*\{.*?\}"
#         toc_pattern = r"\\tableofcontents"
#         begin_doc_pattern = r"\\begin\{document\}"
#
#         begin_match = re.search(begin_doc_pattern, self.tex_content)
#         title_match = re.search(title_pattern, self.tex_content)
#         toc_match = re.search(toc_pattern, self.tex_content)
#
#         # Добавляем титульный лист в структуру, если найден
#         if title_match:
#             self.structure["unnumbered_chapters"].append("титульный лист")
#         else:
#             self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")
#
#         # Добавляем содержание в структуру, если найдено
#         if toc_match:
#             self.structure["unnumbered_chapters"].append("содержание")
#         else:
#             self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")
#
#         # Проверяем порядок следования команд
#         if title_match and begin_match and title_match.start() < begin_match.start():
#             self.errors.append("Ошибка: титульный лист должен подключаться после \\begin{document}.")
#         if title_match and toc_match:
#             between_text = self.tex_content[title_match.end():toc_match.start()]
#             allowed_text = re.sub(r'%.+?\n', '', between_text).strip()
#             if allowed_text and allowed_text != "\\setcounter{page}{2}":
#                 self.errors.append(
#                     "Ошибка: между \\includepdf и \\tableofcontents допускаются только комментарии или \\setcounter{page}{2}.")
#
#     def parse_addcontentsline(self):
#         chapter_star_pattern = re.finditer(r"\\chapter\*\{(.+?)\}", self.tex_content)
#         addcontents_pattern = r"\\addcontentsline\{toc\}\{chapter\}\{(.+?)\}"
#
#         for match in chapter_star_pattern:
#             start_pos = match.end()
#             following_text = self.tex_content[start_pos:]
#             add_match = re.search(addcontents_pattern, following_text)
#             if not add_match or add_match.start() > 100:
#                 self.errors.append(
#                     f"Ошибка: после \\chapter*{{{match.group(1)}}} отсутствует соответствующая команда \\addcontentsline."
#                 )
#
#     def parse_counters(self):
#         pass
#
#     def parse_inroduction(self):
#         pass  # better in checking file
#
#     def parse_refs(self):
#         pass  # better in checking file
