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
                "introduction": self.parse_introduction(),
                "lists": self.parse_lists(),
                "pictures": self.parse_pictures(),
                "tables": self.parse_all_tables()}

    def run_checks(self):
        self.parse_title_and_toc()
        self.parse_addcontentsline()

    def parse_structure(self) -> Dict[str, Any]:
        chapter_titles = re.findall(r'\\chapter\{(.+?)\}', self.tex_content)
        chapters = list(re.finditer(r'\\chapter\{(.+?)\}', self.tex_content))
        numbered_chapters_formatted = [f"{i + 1} глава" for i in range(len(chapter_titles))]

        sections = list(re.finditer(r'\\section\{(.+?)\}', self.tex_content))
        unnumbered_sections = list(re.finditer(r'\\section\*\{(.+?)\}', self.tex_content))

        numbered_sections = {chapter: [] for chapter in numbered_chapters_formatted}
        unnumbered_sections_dict = {chapter: [] for chapter in numbered_chapters_formatted}

        chapter_index = -1
        section_counter = 0
        for section in sections:
            section_title = section.group(1)
            section_pos = section.start()

            while chapter_index + 1 < len(chapters) and chapters[chapter_index + 1].start() < section_pos:
                chapter_index += 1
                section_counter = 0

            if chapter_index >= 0:
                section_counter += 1
                chapter_name = numbered_chapters_formatted[chapter_index]
                numbered_sections[chapter_name].append(f"{chapter_index + 1}.{section_counter} раздел '{section_title}'")

        for section in unnumbered_sections:
            section_title = section.group(1)
            section_pos = section.start()

            chapter_idx = -1
            for idx, chap in enumerate(chapters):
                if chap.start() > section_pos:
                    break
                chapter_idx = idx

            if chapter_idx >= 0:
                chapter_name = numbered_chapters_formatted[chapter_idx]
                unnumbered_sections_dict[chapter_name].append(section_title)

        return {
            "numbered_chapters": numbered_chapters_formatted,
            "unnumbered_chapters": re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content),
            "numbered_sections": numbered_sections,
            "unnumbered_sections": unnumbered_sections_dict,
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
            self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")

        # Добавляем содержание в структуру, если найдено
        if toc_match:
            self.parsed_document["structure"]["unnumbered_chapters"].append("СОДЕРЖАНИЕ")
        else:
            print("no toc")
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

    def parse_introduction(self):
        match = re.search(r'\\chapter\*{ВВЕДЕНИЕ}([\s\S]*?)\\chapter', self.tex_content,
                          re.DOTALL | re.IGNORECASE)
        if not match:
            self.errors.append("Не удалось найти текст введения.")
            return

        introduction_text = match.group(1).lower()
        return introduction_text

    def parse_lists(self):
        list_types = ['enumarabic', 'enumasbuk', 'enummarker']  # +nested maybe
        lists = {list_type: [] for list_type in list_types}

        def find_environment_blocks(content, env_name):
            pattern = re.compile(rf'\\begin\{{{env_name}\}}|\\end\{{{env_name}\}}')
            matches = list(pattern.finditer(content))
            blocks = []

            stack = []
            for match in matches:
                if match.group() == f'\\begin{{{env_name}}}':
                    stack.append(match.start())
                elif match.group() == f'\\end{{{env_name}}}' and stack:
                    start = stack.pop()
                    end = match.end()
                    block = content[start:end]

                    # before = content[:start].rsplit('.', 1)[-1]
                    before_match = re.search(
                        r'((?:\\textbf\{[^}]+?\}|\\bf\s*\{[^}]+?\}|{\\bf\s+[^}]+?}|[^.?!:\n]+[.?!:]))\s*$',
                        content[:start])
                    before_text = before_match.group(1).strip() if before_match else ""
                    full_block = f"{before_text}\n{block}".strip()
                    blocks.append(full_block)

            return blocks

        for list_type in list_types:
            env_blocks = find_environment_blocks(self.tex_content, list_type)
            lists[list_type].extend(env_blocks)

        return lists

    def parse_pictures(self):
        return {
            "labels": self.parse_picture_labels(),
            "refs": self.parse_picture_refs()
        }

    def parse_picture_labels(self):
        labels = []

        # Собираем \label внутри \begin{figure}...\end{figure}
        figure_envs = re.finditer(r'\\begin\{figure\}.*?\\end\{figure\}', self.tex_content, re.DOTALL)
        for env in figure_envs:
            content = env.group(0)
            start_pos = env.start()

            for match in re.finditer(r'\\label\{([^\}]+)\}', content):
                labels.append({
                    "label": match.group(1),
                    "position": start_pos + match.start()
                })

        # Добавляем \label из \myfigure
        for match in re.finditer(r'\\myfigure\{.*?\}\{.*?\}\{.*?\}\{([^\}]+)\}', self.tex_content):
            labels.append({
                "label": match.group(1),
                "position": match.start()
            })

        return labels

    def parse_picture_refs(self):
        refs = []

        for match in re.finditer(r'\\ref\{fig:([^\}]+)\}', self.tex_content):
            refs.append({
                "label": match.group(1),
                "position": match.start()
            })

        return refs

    def parse_all_tables(self):
        tables_data = {
            "tables": {
                "labels": [],
                "refs": [],
                "contents": []
            },
            "longtables": {
                "labels": [],
                "refs": [],
                "contents": []
            }
        }

        # Ссылки на обычные таблицы
        for match in re.finditer(r'\\ref\{table:([^\}]+)\}', self.tex_content):
            tables_data["tables"]["refs"].append({
                "label": match.group(1),
                "position": match.start()
            })

        # Ссылки на длинные таблицы
        for match in re.finditer(r'\\ref\{longtable:([^\}]+)\}', self.tex_content):
            tables_data["longtables"]["refs"].append({
                "label": match.group(1),
                "position": match.start()
            })

        # Обычные таблицы
        for env in re.finditer(r'\\begin\{table\}.*?\\end\{table\}', self.tex_content, re.DOTALL):
            block = env.group(0)
            start_pos = env.start()
            tables_data["tables"]["contents"].append({
                "content": block,
                "position": start_pos
            })
            for label_match in re.finditer(r'\\label\{table:([^\}]+)\}', block):
                tables_data["tables"]["labels"].append({
                    "label": label_match.group(1),
                    "position": start_pos + label_match.start()
                })

        # Длинные таблицы
        for env in re.finditer(r'\\begin\{longtable\}.*?\\end\{longtable\}', self.tex_content, re.DOTALL):
            block = env.group(0)
            start_pos = env.start()
            tables_data["longtables"]["contents"].append({
                "content": block,
                "position": start_pos
            })
            for label_match in re.finditer(r'\\label\{longtable:([^\}]+)\}', block):
                tables_data["longtables"]["labels"].append({
                    "label": label_match.group(1),
                    "position": start_pos + label_match.start()
                })

        return tables_data

    # def parse_all_tables(self):
    #     all_tables = {
    #         "tables": [],
    #         "longtables": []
    #     }
    #
    #     ref_pattern = r'\\ref\{table:[^}]+\}'
    #     table_pattern = r'\\begin\{table\}[\s\S]*?\\end\{table\}'
    #     longtable_pattern = r'\\begin\{longtable\}[\s\S]*?\\end\{longtable\}'
    #
    #     for ref_match in re.finditer(ref_pattern, self.tex_content):
    #         start_pos = ref_match.start()
    #         table_fragment = None
    #
    #         longtable_match = re.search(longtable_pattern, self.tex_content[start_pos:])
    #         table_match = re.search(table_pattern, self.tex_content[start_pos:])
    #
    #         # Выбираем тот блок, который встречается раньше
    #         if longtable_match and (not table_match or longtable_match.start() < table_match.start()):
    #             end_pos = start_pos + longtable_match.end()
    #             table_fragment = self.tex_content[start_pos:end_pos].strip()
    #             all_tables["longtables"].append(table_fragment)
    #         elif table_match:
    #             end_pos = start_pos + table_match.end()
    #             table_fragment = self.tex_content[start_pos:end_pos].strip()
    #             all_tables["tables"].append(table_fragment)
    #         else:
    #             self.errors.append(
    #                 f"После ссылки {ref_match.group()} не найдена соответствующая таблица (\\begin{{table}} или \\begin{{longtable}})."
    #             )
    #
    #     return all_tables

    # def parse_all_tables(self):
    #     result = {"tables": [], "longtables": []}
    #
    #     def extract_tables(env_name):
    #         pattern = re.compile(rf'\\begin\{{{env_name}\}}[\s\S]*?\\end\{{{env_name}\}}')
    #         return pattern.findall(self.tex_content)
    #
    #     result["tables"] = extract_tables("table")
    #     result["longtables"] = extract_tables("longtable")
    #     return result
    #
    # def check_duplicate_labels(self):
    #     labels = re.findall(r'\\label\{([^}]+)\}', self.tex_content)
    #     duplicates = set(label for label in labels if labels.count(label) > 1)
    #     for dup in duplicates:
    #         self.errors.append(f"Дублирующийся label: \\label{{{dup}}} встречается несколько раз.")

