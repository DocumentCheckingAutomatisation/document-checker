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
                "all_tables": self.parse_all_tables()}

    def run_checks(self):
        self.parse_title_and_toc()
        self.parse_addcontentsline()
        self.parse_counters()

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
                numbered_sections[chapter_name].append(f"{chapter_index + 1}.{section_counter} раздел")

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
            # self.errors.append("Ошибка: титульный лист не найден или подключен неверной командой.")

        # Добавляем содержание в структуру, если найдено
        if toc_match:
            self.parsed_document["structure"]["unnumbered_chapters"].append("содержание")
        else:
            print("no toc")
            # self.errors.append("Ошибка: отсутствует \\tableofcontents после титульного листа.")

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
                    before_match = re.search(r'([^.?!:\n]+[.?!:])\s*$', content[:start])
                    before_text = before_match.group(1).strip() if before_match else ""
                    full_block = f"{before_text}\n{block}".strip()
                    blocks.append(full_block)

            return blocks

        for list_type in list_types:
            env_blocks = find_environment_blocks(self.tex_content, list_type)
            lists[list_type].extend(env_blocks)

        return lists

    def parse_pictures(self):
        pictures = []

        # Шаг 1: Найдём все ссылки на рисунки
        link_pattern = r"\(рис\.\\ref\{(?P<label>fig:[^}]+)\}\)"
        links = [
            {"type": "link", "label": match.group("label"), "pos": match.start()}
            for match in re.finditer(link_pattern, self.tex_content)
        ]

        # Шаг 2: Найдём все вставки рисунков
        insertions = []

        # Вариант 1: \myfigure{ширина}{файл}{подпись}{label}
        myfigure_pattern = r"\\myfigure\{.*?\}\{.*?\}\{.*?\}\{(?P<label>[^}]+)\}"
        for match in re.finditer(myfigure_pattern, self.tex_content):
            insertions.append({
                "type": "figure",
                "label": match.group("label"),
                "pos": match.start()
            })

        # Вариант 2: \begin{figure}...\label{fig:xxx}...\end{figure}
        figure_env_pattern = r"\\begin\{figure\}.*?\\label\{(?P<label>fig:[^}]+)\}.*?\\end\{figure\}"
        for match in re.finditer(figure_env_pattern, self.tex_content, re.DOTALL):
            insertions.append({
                "type": "figure",
                "label": match.group("label"),
                "pos": match.start()
            })

        # Шаг 3: Объединяем все объекты и связываем
        all_items = links + insertions
        all_items.sort(key=lambda x: x["pos"])

        used_links = set()
        used_figures = set()

        for i, item in enumerate(all_items):
            if item["type"] == "link":
                # ищем ближайший figure с такой же меткой
                for j in range(i + 1, len(all_items)):
                    other = all_items[j]
                    if other["type"] == "figure" and other["label"] == item["label"] and other[
                        "label"] not in used_figures:
                        pictures.append({
                            "label": item["label"],
                            "link_pos": item["pos"],
                            "figure_pos": other["pos"],
                            "distance": other["pos"] - item["pos"]
                        })
                        used_links.add(item["label"])
                        used_figures.add(other["label"])
                        break
                else:
                    # не нашли рисунка
                    pictures.append({
                        "label": item["label"],
                        "link_pos": item["pos"],
                        "figure_pos": None,
                        "distance": None
                    })

            elif item["type"] == "figure":
                if item["label"] not in used_figures:
                    # ищем ссылку ДО рисунка
                    for j in range(i - 1, -1, -1):
                        other = all_items[j]
                        if other["type"] == "link" and other["label"] == item["label"] and other[
                            "label"] not in used_links:
                            break
                    else:
                        # не нашли ссылку
                        pictures.append({
                            "label": item["label"],
                            "link_pos": None,
                            "figure_pos": item["pos"],
                            "distance": None
                        })

        return pictures

    def parse_all_tables(self):
        all_tables = {
            "tables": [],
            "longtables": []
        }

        ref_pattern = r'\\ref\{table:[^}]+\}'
        table_pattern = r'\\begin\{table\}[\s\S]*?\\end\{table\}'
        longtable_pattern = r'\\begin\{longtable\}[\s\S]*?\\end\{longtable\}'

        for ref_match in re.finditer(ref_pattern, self.tex_content):
            start_pos = ref_match.start()
            table_fragment = None

            longtable_match = re.search(longtable_pattern, self.tex_content[start_pos:])
            table_match = re.search(table_pattern, self.tex_content[start_pos:])

            # Выбираем тот блок, который встречается раньше
            if longtable_match and (not table_match or longtable_match.start() < table_match.start()):
                end_pos = start_pos + longtable_match.end()
                table_fragment = self.tex_content[start_pos:end_pos].strip()
                all_tables["longtables"].append(table_fragment)
            elif table_match:
                end_pos = start_pos + table_match.end()
                table_fragment = self.tex_content[start_pos:end_pos].strip()
                all_tables["tables"].append(table_fragment)
            else:
                self.errors.append(
                    f"После ссылки {ref_match.group()} не найдена соответствующая таблица (\\begin{{table}} или \\begin{{longtable}})."
                )

        return all_tables

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

    def parse_counters(self):
        pass
