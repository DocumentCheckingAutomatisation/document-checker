import os
import re
from typing import Dict, Any

from src.core.doc_type import DocType
from src.logics.parsers.latex_parser import LatexParser
from src.logics.rule_service import RuleService


class LatexChecker:
    def __init__(self, tex_file, sty_file, doc_type: str):
        parser = LatexParser(tex_file)
        self.parsed_document = parser.parsed_document
        self.errors = parser.errors
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])
        self.sty_file = self.sty_content = sty_file.read().decode("utf-8").splitlines() if sty_file else []

    def check_document(self) -> Dict[str, Any]:
        self.check_structure()
        self.check_introduction_keywords()
        self.check_sty_file()
        return {"valid": not bool(self.errors), "errors": self.errors}

    def check_structure(self):
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        required_sections = self.rules["structure_rules"].get("required_sections", {})

        # Проверка глав
        all_chapters = [ch.lower() for ch in
                        self.parsed_document["structure"]["numbered_chapters"] +
                        self.parsed_document["structure"]["unnumbered_chapters"]]

        for chapter in required_chapters:
            if not any(chapter in parsed_ch for parsed_ch in all_chapters):
                self.errors.append(f"Отсутствует обязательная глава: {chapter}")

        # Проверка разделов
        all_numbered_sections = self.parsed_document["structure"].get("numbered_sections", {})
        all_unnumbered_sections = self.parsed_document["structure"].get("unnumbered_sections", {})

        for chapter, sections in required_sections.items():
            chapter_key = f"{chapter} глава"
            found_sections = set()

            # Получаем все разделы для данной главы
            if chapter_key in all_numbered_sections:
                found_sections.update([sec.lower() for sec in all_numbered_sections[chapter_key]])
            if chapter_key in all_unnumbered_sections:
                found_sections.update([sec.lower() for sec in all_unnumbered_sections[chapter_key]])

            # Проверяем наличие необходимых разделов
            for section in sections:
                if section.lower() not in found_sections:
                    self.errors.append(f"В главе {chapter} отсутствует раздел: {section}")

    def check_introduction_keywords(self):
        introduction_keywords = self.rules["structure_rules"].get("introduction_keywords", [])

        for keyword in introduction_keywords:

            if keyword not in self.parsed_document["introduction"]:
                print(keyword)
                self.errors.append(f"Отсутствует ключевое слово во введении: {keyword}")

    def check_sty_file(self):
        rules_dir = os.path.join(os.path.dirname(__file__), "../../..", "docs")
        reference_sty_path = os.path.join(rules_dir, "settings.sty")

        try:
            with open(reference_sty_path, "r", encoding="utf-8") as ref_file:
                reference_lines = ref_file.readlines()
        except FileNotFoundError:
            self.errors.append("Файл settings.sty не найден в папке docs.")
            return

        uploaded_lines = self.sty_content

        if not uploaded_lines:
            self.errors.append("Файл settings.sty не был загружен или пуст.")
            return

        def remove_comments_and_empty_lines(lines):
            cleaned_lines = []
            for line in lines:
                line = line.split('%', 1)[0].strip()
                if line:
                    cleaned_lines.append(line)
            return cleaned_lines

        reference_lines = remove_comments_and_empty_lines(reference_lines)
        uploaded_lines = remove_comments_and_empty_lines(uploaded_lines)

        for i, (ref_line, uploaded_line) in enumerate(zip(reference_lines, uploaded_lines), start=1):
            if ref_line.strip() != uploaded_line.strip():
                self.errors.append(
                    f"Несовпадение в settings.sty: ожидалось '{ref_line.strip()}', получено '{uploaded_line.strip()}'"
                )

        if len(uploaded_lines) < len(reference_lines):
            self.errors.append(
                f"Файл settings.sty содержит только {len(uploaded_lines)} строк, ожидалось {len(reference_lines)}."
            )
        elif len(uploaded_lines) > len(reference_lines):
            self.errors.append(
                f"Файл settings.sty содержит {len(uploaded_lines)} строк, что больше ожидаемых {len(reference_lines)}."
            )

    def check_lists(self):
        lists = self.parsed_document.get("lists", {})

        for list_type, entries in lists.items():
            for full_list in entries:
                is_nested = bool(re.search(r"\\begin\{enum[a-z]+\}.*?\\begin\{enum[a-z]+\}", full_list, re.DOTALL))
                if is_nested:
                    self.check_nested_list(full_list)
                else:
                    self.check_regular_list(full_list)

    def check_regular_list(self, content: str):
        match_before = re.search(r"(.+?)\\begin\{enum[a-z]+\}", content, re.DOTALL)
        intro = match_before.group(1).strip() if match_before else ""
        items = re.findall(r"\\item (.+?)(?=(\\item|\\end\{))", content, re.DOTALL)
        items = [item[0].strip() for item in items]

        if not items:
            return

        intro_end = intro[-1] if intro else ""
        for i, item in enumerate(items):
            if intro_end == ":":
                if not item[0].islower():
                    self.errors.append(
                        "Пункт должен начинаться с маленькой буквы (вводная часть заканчивается на ':').")
                if i < len(items) - 1 and not item.endswith(";"):
                    self.errors.append("Промежуточный пункт должен оканчиваться на ';'.")
                if i == len(items) - 1 and not item.endswith("."):
                    self.errors.append("Последний пункт должен оканчиваться на '.'.")
            elif intro_end == ".":
                if not item[0].isupper():
                    self.errors.append("Пункт должен начинаться с большой буквы (вводная часть заканчивается на '.').")
                if not item.endswith("."):
                    self.errors.append("Каждый пункт должен заканчиваться на '.'.")

    def check_nested_list(self, content: str):
        top_items = re.split(r"\\item", content)
        for i, top in enumerate(top_items[1:]):
            top = top.strip()
            match_intro = re.match(r"(.+?):", top)
            if not match_intro:
                self.errors.append("Во вложенном списке каждый верхнеуровневый элемент должен заканчиваться на ':'.")
                continue

            nested_items = re.findall(r"\\item (.+?)(?=(\\item|\\end\{))", top, re.DOTALL)
            nested_items = [item[0].strip() for item in nested_items]

            for j, subitem in enumerate(nested_items):
                if j < len(nested_items) - 1 and not subitem.endswith(";"):
                    self.errors.append("Промежуточный пункт вложенного списка должен заканчиваться на ';'.")
                if j == len(nested_items) - 1 and not subitem.endswith("."):
                    self.errors.append("Последний пункт вложенного списка должен заканчиваться на '.'.")
