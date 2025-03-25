import re
from typing import Dict, Any


class LatexParser:
    def __init__(self, tex_file):
        self.tex_content = self.remove_comments(tex_file.read().decode("utf-8"))
        self.errors = []
        self.parsed_document = self.run_parse()
        self.run_checks()

    @staticmethod
    def remove_comments(content: str) -> str:
        """Удаляет строки, начинающиеся с %, и текст после % в строках"""
        return re.sub(r'(?<!\\)%.*', '', content)

    def run_parse(self):
        return {"structure": self.parse_structure(),
                "introduction": self.parse_introduction()}

    def run_checks(self):
        self.parse_title_and_toc()
        self.parse_addcontentsline()
        self.parse_counters()
        self.parse_refs()

    def parse_structure(self) -> Dict[str, Any]:
        # Найдем все нумерованные главы и их заголовки
        chapter_titles = re.findall(r'\\chapter\{(.+?)\}', self.tex_content)
        chapters = list(re.finditer(r'\\chapter\{(.+?)\}', self.tex_content))

        numbered_chapters_formatted = [f"{i + 1} глава" for i in range(len(chapter_titles))]

        # Найдем все нумерованные разделы с их заголовками и позициями
        sections = list(re.finditer(r'\\section\{(.+?)\}', self.tex_content))

        # Сформируем список с номерами разделов, например "1.1 Название раздела"
        numbered_sections = []
        chapter_index = 0
        section_counter = 0

        for section in sections:
            section_title = section.group(1)
            section_pos = section.start()

            # Проверяем, относится ли этот раздел к новой главе
            while chapter_index < len(chapters) and chapters[chapter_index].start() < section_pos:
                chapter_index += 1
                section_counter = 0  # Обнуляем счетчик разделов при переходе к новой главе

            section_counter += 1
            numbered_sections.append(f"{chapter_index}.{section_counter} раздел")

        return {
            "numbered_chapters": numbered_chapters_formatted,
            "unnumbered_chapters": re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content),
            "numbered_sections": numbered_sections,
            "unnumbered_sections": re.findall(r'\\section\*\{(.+?)\}', self.tex_content),
        }

    def parse_title_and_toc(self):
        title_pattern = r"\\includepdf.*\{.*?\}"
        toc_pattern = r"\\tableofcontents"
        begin_doc_pattern = r"\\begin\{document\}"

        begin_match = re.search(begin_doc_pattern, self.tex_content)
        title_match = re.search(title_pattern, self.tex_content)
        toc_match = re.search(toc_pattern, self.tex_content)

        # Добавляем титульный лист в структуру, если найден
        if title_match:
            self.parsed_document["structure"]["unnumbered_chapters"].append("титульный лист")
        else:
            print("no title")
            #self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")

        # Добавляем содержание в структуру, если найдено
        if toc_match:
            self.parsed_document["structure"]["unnumbered_chapters"].append("содержание")
        else:
            print("no toc")
            #self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")

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

    def parse_refs(self):
        pass  # better in checking file

    def parse_introduction(self):
        match = re.search(r'\\chapter\*{ВВЕДЕНИЕ}([\s\S]*?)\\chapter', self.tex_content,
                          re.DOTALL | re.IGNORECASE)
        if not match:
            self.errors.append("Не удалось найти текст введения.")
            return

        introduction_text = match.group(1).lower()
        return introduction_text
