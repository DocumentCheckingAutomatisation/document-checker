import re
from typing import Dict, Any


class LatexParser:
    def __init__(self, tex_file):
        self.tex_content = tex_file.read().decode("utf-8")
        self.structure = self.parse_structure()
        self.errors = []

    def parse_structure(self) -> Dict[str, Any]:
        chapters = self.parse_chapters()
        sections = self.parse_sections()

        parsed_structure = {**chapters, **sections}

        return parsed_structure

    def parse_chapters(self):
        numbered_chapters = re.findall(r'\\chapter\{(.+?)\}', self.tex_content)
        unnumbered_chapters = re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content)
        parsed_chapters = {"numbered_chapters": numbered_chapters, "unnumbered_chapters": unnumbered_chapters}
        return parsed_chapters

    def parse_sections(self):
        numbered_sections = re.findall(r'\\section\{(.+?)\}', self.tex_content)
        unnumbered_sections = re.findall(r'\\section\*\{(.+?)\}', self.tex_content)
        parsed_sections = {"numbered_sections": numbered_sections, "unnumbered_sections": unnumbered_sections}
        return parsed_sections

    def parse_inroduction(self):
        pass # better in checking file

    def parse_tableofcontents(self):
        title_pattern = r"\\includepdf.*\{.*?\}"
        toc_pattern = r"\\tableofcontents"
        setcounter_pattern = r"\\setcounter\{page\}\{2\}"

        title_match = re.search(title_pattern, self.tex_content)
        toc_match = re.search(toc_pattern, self.tex_content)

        if not title_match:
            self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")
        elif not toc_match:
            self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")
        else:
            between_text = self.tex_content[title_match.end():toc_match.start()]
            allowed_text = re.sub(r'%.+?\n', '', between_text).strip()
            if allowed_text and allowed_text != "\\setcounter{page}{2}":
                self.errors.append(
                    "Ошибка: между \\includepdf и \\tableofcontents допускаются только комментарии или \\setcounter{page}{2}.")

        return self.errors

    def parse_addcontentsline(self):
        chapter_star_pattern = re.finditer(r"\\chapter\*\{(.+?)\}", self.tex_content)
        addcontents_pattern = r"\\addcontentsline\{toc\}\{chapter\}\{(.+?)\}"

        for match in chapter_star_pattern:
            start_pos = match.end()
            following_text = self.tex_content[start_pos:]
            add_match = re.search(addcontents_pattern, following_text)
            if not add_match or add_match.start() > 100:
                self.errors.append(
                    f"Ошибка: после \\chapter*{{{match.group(1)}}} отсутствует соответствующая команда \\addcontentsline.")

        return self.errors

    def parse_title(self):
        title_pattern = r"\\includepdf.*\{.*?\}"
        begin_doc_pattern = r"\\begin\{document\}"

        # Найти позиции команд
        begin_match = re.search(begin_doc_pattern, self.tex_content)
        title_match = re.search(title_pattern, self.tex_content)

        if not title_match:
            self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")
        elif not begin_match:
            self.errors.append("Ошибка: отсутствует \\begin{document}.")
        else:
            # Проверка порядка следования команд
            if title_match.start() < begin_match.start():
                self.errors.append("Ошибка: титульный лист должен подключаться после \\begin{document}.")
            else:
                # Проверка наличия только комментариев между \\begin{document} и \\includepdf
                between_text = self.tex_content[begin_match.end():title_match.start()]
                if re.sub(r'%.+?\n', '', between_text).strip():
                    self.errors.append("Ошибка: между \\begin{document} и \\includepdf допускаются только комментарии.")

        return self.errors

    def parse_title_and_toc(self):
        title_pattern = r"\\includepdf.*\{.*?\}"
        toc_pattern = r"\\tableofcontents"
        begin_doc_pattern = r"\\begin\{document\}"

        # Найти позиции команд
        begin_match = re.search(begin_doc_pattern, self.tex_content)
        title_match = re.search(title_pattern, self.tex_content)
        toc_match = re.search(toc_pattern, self.tex_content)

        # Проверка наличия ключевых элементов
        if not title_match:
            self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")
        if not begin_match:
            self.errors.append("Ошибка: отсутствует \\begin{document}.")
        if not toc_match:
            self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")

        if title_match and begin_match:
            # Проверка порядка следования команд
            if title_match.start() < begin_match.start():
                self.errors.append("Ошибка: титульный лист должен подключаться после \\begin{document}.")
            else:
                # Проверка наличия только комментариев между \\begin{document} и \\includepdf
                between_text = self.tex_content[begin_match.end():title_match.start()]
                if re.sub(r'%.+?\n', '', between_text).strip():
                    self.errors.append("Ошибка: между \\begin{document} и \\includepdf допускаются только комментарии.")

        if title_match and toc_match:
            # Проверка наличия только комментариев или \\setcounter{page}{2} между \\includepdf и \\tableofcontents
            between_text = self.tex_content[title_match.end():toc_match.start()]
            allowed_text = re.sub(r'%.+?\n', '', between_text).strip()
            if allowed_text and allowed_text != "\\setcounter{page}{2}":
                self.errors.append(
                    "Ошибка: между \\includepdf и \\tableofcontents допускаются только комментарии или \\setcounter{page}{2}.")

    def parse_counters(self):
        pass

    def parse_refs(self):
        pass # better in checking file
