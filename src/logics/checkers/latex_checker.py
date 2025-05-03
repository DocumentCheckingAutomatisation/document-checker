import os
import re
from typing import Dict, Any

from src.core.doc_type import DocType
from src.logics.parsers.latex_parser import LatexParser
from src.logics.rule_service import RuleService


class LatexChecker:
    def __init__(self, tex_file, sty_file, doc_type: str, deduplicate_errors: bool = True):
        parser = LatexParser(tex_file)
        self.parsed_document = parser.parsed_document
        self.errors = parser.errors
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])
        self.sty_file = self.sty_content = sty_file.read().decode("utf-8").splitlines() if sty_file else []

        self.deduplicate_errors = deduplicate_errors
        self._error_set = set() if deduplicate_errors else None

    def add_error(self, message: str):
        if self.deduplicate_errors:
            if message not in self._error_set:
                self.errors.append(message)
                self._error_set.add(message)
        else:
            self.errors.append(message)

    def check_document(self) -> Dict[str, Any]:
        self.check_structure()
        self.check_introduction_keywords()
        self.check_sty_file()
        self.check_lists()
        self.check_pictures()
        self.check_tables()
        self.check_appendices()
        self.check_bibliography()

        found_elements = self.get_found_elements()

        return {"valid": not bool(self.errors), "found": found_elements, "errors": self.errors}

    def check_structure(self):
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        required_sections = self.rules["structure_rules"].get("required_sections", {})

        # Проверка глав
        all_chapters = [ch for ch in
                        self.parsed_document["structure"]["numbered_chapters"] +
                        self.parsed_document["structure"]["unnumbered_chapters"]]

        for chapter in required_chapters:
            if not any(chapter in parsed_ch for parsed_ch in all_chapters):
                self.add_error(f"Отсутствует обязательная глава: {chapter}")

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
            for required_section in sections:
                required_section_lower = required_section.lower()
                if not any(required_section_lower in found for found in found_sections):
                    self.add_error(f"В главе {chapter} отсутствует раздел: {required_section}")

    def check_introduction_keywords(self):
        introduction_keywords = self.rules["structure_rules"].get("introduction_keywords", [])

        # Приводим жирные фразы к нижнему регистру и убираем двоеточия
        bold_phrases = [phrase.lower().rstrip(":") for phrase in self.parsed_document.get("introduction", [])]
        for keyword in introduction_keywords:
            keyword_clean = keyword.lower().rstrip(":")
            if all(keyword_clean not in phrase for phrase in bold_phrases):
                self.add_error(f"Отсутствует ключевое слово во введении, которое должно быть выделено командой жирности {{\\bf}}: {keyword}")

    def check_sty_file(self):
        rules_dir = os.path.join(os.path.dirname(__file__), "../../..", "docs")
        reference_sty_path = os.path.join(rules_dir, "settings.sty")

        try:
            with open(reference_sty_path, "r", encoding="utf-8") as ref_file:
                reference_lines = ref_file.readlines()
        except FileNotFoundError:
            self.add_error("Файл settings.sty не найден в папке docs.")
            return

        uploaded_lines = self.sty_content

        if not uploaded_lines:
            self.add_error("Файл settings.sty не был загружен или пуст.")
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
                self.add_error(
                    f"Несовпадение в settings.sty: ожидалось '{ref_line.strip()}', получено '{uploaded_line.strip()}'"
                )

        if len(uploaded_lines) < len(reference_lines):
            self.add_error(
                f"Файл settings.sty содержит только {len(uploaded_lines)} строк, ожидалось {len(reference_lines)}."
            )
        elif len(uploaded_lines) > len(reference_lines):
            self.add_error(
                f"Файл settings.sty содержит {len(uploaded_lines)} строк, что больше ожидаемых {len(reference_lines)}."
            )

    @staticmethod
    def short(item: str, max_len: int = 60) -> str:
        item = item.replace("\n", " ").strip()
        return (item[:max_len] + "...") if len(item) > max_len else item

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

        # Удаляем LaTeX-команды и внешние скобки, чтобы определить, чем заканчивается вводная часть
        clean_intro = re.sub(r"{\\bf\s+([^}]+)}", r"\1", intro)  # {\bf ...} → ...
        clean_intro = re.sub(r"\\textbf\{([^}]+)\}", r"\1", clean_intro)  # \textbf{...} → ...
        clean_intro = re.sub(r"\\[a-zA-Z]+\s*", "", clean_intro)  # удалить остальные команды
        clean_intro = re.sub(r"{|}", "", clean_intro).strip()

        intro_end = clean_intro[-1] if clean_intro else ""

        for i, item in enumerate(items):
            item_preview = self.short(item)
            if intro_end == ":":
                if not item[0].islower():
                    self.add_error(
                        f"Пункт должен начинаться с маленькой буквы (т.к. вводная часть заканчивается на ':') --> '{item_preview}'")
                if i < len(items) - 1 and not item.endswith(";"):
                    self.add_error(
                        f"Промежуточный пункт должен оканчиваться на ';' --> '{item_preview}'")
                if i == len(items) - 1 and not item.endswith("."):
                    self.add_error(
                        f"Последний пункт должен оканчиваться на '.' --> '{item_preview}'")
            elif intro_end == ".":
                if not item[0].isupper():
                    self.add_error(
                        f"Пункт должен начинаться с большой буквы (т.к. вводная часть заканчивается на '.') --> '{item_preview}'")
                if not item.endswith("."):
                    self.add_error(
                        f"Каждый пункт должен заканчиваться на '.' --> '{item_preview}'")
            else:
                self.add_error(
                    f"Вводная часть перед списком должна заканчиваться ':' или '.' --> '{self.short(intro)}'")

    def check_nested_list(self, content: str):
        top_items = re.split(r"\\item", content)
        for i, top in enumerate(top_items[1:]):
            top = top.strip()

            # Очистка от \bf, \textbf, других команд и фигурных скобок
            clean_top = re.sub(r"{\\bf\s+([^}]+)}", r"\1", top)
            clean_top = re.sub(r"\\textbf\{([^}]+)\}", r"\1", clean_top)
            clean_top = re.sub(r"\\[a-zA-Z]+\s*", "", clean_top)
            clean_top = re.sub(r"{|}", "", clean_top).strip()

            # Проверка окончания верхнего уровня
            if not clean_top.endswith(":"):
                self.add_error(
                    f"Во вложенном списке каждый верхнеуровневый элемент должен оканчиваться на ':'"
                    f" Фрагмент: '{self.short(top)}'"
                )
                continue

            # Извлечение вложенных пунктов
            nested_items = re.findall(r"\\item (.+?)(?=(\\item|\\end\{))", top, re.DOTALL)
            nested_items = [item[0].strip() for item in nested_items]

            for j, subitem in enumerate(nested_items):
                subitem_preview = self.short(subitem)
                if j < len(nested_items) - 1 and not subitem.endswith(";"):
                    self.add_error(
                        f"Промежуточный пункт вложенного списка должен оканчиваться на ';' --> '{subitem_preview}'")
                if j == len(nested_items) - 1 and not subitem.endswith("."):
                    self.add_error(
                        f"Последний пункт вложенного списка должен оканчиваться на '.' --> '{subitem_preview}'")

    # def check_nested_list(self, content: str):
    #
    #     top_items = re.split(r"\\item", content)
    #     for i, top in enumerate(top_items[1:]):
    #         top = top.strip()
    #         match_intro = re.match(r"(.+?):", top)
    #
    #         if not match_intro:
    #             self.add_error(
    #                 f"Во вложенном списке каждый верхнеуровневый элемент должен оканчиваться на ':'"
    #                 f"Фрагмент: '{self.short(top)}'")
    #             continue
    #
    #         nested_items = re.findall(r"\\item (.+?)(?=(\\item|\\end\{))", top, re.DOTALL)
    #         nested_items = [item[0].strip() for item in nested_items]
    #
    #         for j, subitem in enumerate(nested_items):
    #             subitem_preview = self.short(subitem)
    #             if j < len(nested_items) - 1 and not subitem.endswith(";"):
    #                 self.add_error(
    #                     f"Промежуточный пункт вложенного списка должен оканчиваться на ';' --> '{subitem_preview}'")
    #             if j == len(nested_items) - 1 and not subitem.endswith("."):
    #                 self.add_error(
    #                     f"Последний пункт вложенного списка должен оканчиваться на '.' --> '{subitem_preview}'")

    def check_pictures(self):
        labels = self.parsed_document["pictures"]["labels"]
        refs = self.parsed_document["pictures"]["refs"]

        labels_by_name = {lbl["label"]: lbl["position"] for lbl in labels}
        refs_by_name = {ref["label"]: ref["position"] for ref in refs}

        # Проверка наличия ссылки для каждого рисунка
        for label, label_pos in labels_by_name.items():
            if label not in refs_by_name:
                self.add_error(f"Нет ссылки на рисунок с меткой: {label}")

        # Проверка наличия рисунка для каждой ссылки
        for ref, ref_pos in refs_by_name.items():
            if ref not in labels_by_name:
                self.add_error(f"Нет рисунка с меткой: {ref}")
            else:
                label_pos = labels_by_name[ref]
                if ref_pos > label_pos:
                    self.add_error(f"Ссылка на рисунок \\ref{{{ref}}} находится после самого рисунка")
                elif label_pos - ref_pos > 1800:
                    self.add_error(
                        f"Слишком большое расстояние между ссылкой \\ref{{{ref}}} и таблицей. Убедитесь, что таблица расположена на той же или следующей странице")

    def check_tables(self):
        for table_type in ["tables", "longtables"]:
            labels = self.parsed_document["tables"][table_type]["labels"]
            refs = self.parsed_document["tables"][table_type]["refs"]

            labels_by_name = {lbl["label"]: lbl["position"] for lbl in labels}
            refs_by_name = {ref["label"]: ref["position"] for ref in refs}

            # Проверка: на таблицу есть label, но нет ссылки
            for label, label_pos in labels_by_name.items():
                if label not in refs_by_name:
                    self.add_error(f"Нет ссылки на {table_type[:-1]} с меткой: {label}")

            # Проверка: есть ссылка, но нет таблицы с таким label
            for ref, ref_pos in refs_by_name.items():
                if ref not in labels_by_name:
                    self.add_error(f"Нет {table_type[:-1]} с меткой: {ref}")
                else:
                    label_pos = labels_by_name[ref]
                    if ref_pos > label_pos:
                        self.add_error(f"Ссылка на {table_type[:-1]} \\ref{{{ref}}} находится после самой таблицы")
                    elif label_pos - ref_pos > 1800:
                        self.add_error(
                            f"Слишком большое расстояние между ссылкой \\ref{{{ref}}} и таблицей. Убедитесь, что таблица расположена на той же или следующей странице")

    def check_appendices(self):
        appendices = self.parsed_document["appendices"]
        titles_by_letter = {item["letter"]: item for item in appendices["appendix_titles"]}
        links_by_letter = {link["letter"]: link for link in appendices["appendix_links"]}

        # Проверка: есть приложение, но нет ссылки
        for letter, title in titles_by_letter.items():
            # Если это приложение А с PDF, пропускаем
            if letter == "А" and title.get("pdf_included"):
                self.errors.remove("Отсутствует обязательная глава: ПРИЛОЖЕНИЯ")
                continue
            if letter not in links_by_letter:
                self.add_error(f"Нет ссылки на приложение {letter}")

        # Проверка: есть ссылка, но нет приложения
        for letter in links_by_letter:
            if letter not in titles_by_letter:
                self.add_error(f"Есть ссылка на несуществующее приложение {letter}")

    #
    # def check_appendices(self):
    #     appendices = self.parsed_document["appendices"]
    #     titles_by_letter = {item["letter"]: item for item in appendices["appendix_titles"]}
    #     links_by_letter = {link["letter"]: link for link in appendices["appendix_links"]}
    #
    #     # Проверка: есть приложение, но нет ссылки
    #     for letter in titles_by_letter:
    #         if letter not in links_by_letter:
    #             self.add_error(f"Нет ссылки на приложение {letter}")
    #
    #     # Проверка: есть ссылка, но нет приложения
    #     for letter in links_by_letter:
    #         if letter not in titles_by_letter:
    #             self.add_error(f"Есть ссылка на несуществующее приложение {letter}")

        # # Удаление ошибок при типе practice_report
        # if self.rules.get("doc_type") == "practice_report":
        #     self.errors = [
        #         e for e in self.errors
        #         if e not in [
        #             "Отсутствует обязательная глава: ПРИЛОЖЕНИЯ",
        #             "Нет ссылки на приложение А"
        #         ]
        #     ]
        #     if self.deduplicate_errors:
        #         self._error_set.discard("Отсутствует обязательная глава: ПРИЛОЖЕНИЯ")
        #         self._error_set.discard("Нет ссылки на приложение А")



    def check_bibliography(self):
        bib_data = self.parsed_document["bibliography"]
        cited_keys = set(bib_data["cite_keys"])
        item_keys = {item["key"] for item in bib_data["bibliography_items"]}

        # Есть ссылка \cite, но нет \bibitem
        for key in cited_keys:
            if key not in item_keys:
                self.add_error(f"Есть ссылка \\cite{{{key}}}, но нет элемента библиографии с таким ключом")

        # Есть элемент \bibitem, но нет \cite
        for key in item_keys:
            if key not in cited_keys:
                self.add_error(f"Элемент библиографии с ключом {key} не используется в тексте через \\cite{{{key}}}")


