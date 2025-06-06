import re
from typing import Dict, Any

from src.core.doc_type import DocType
from src.logics.parsers.docx_parser import DocxParser
from src.logics.rule_service import RuleService


class DocxChecker:
    def __init__(self, docx_file_path, doc_type: str, deduplicate_errors: bool = True):
        parser = DocxParser(docx_file_path)
        self.parsed_document = parser.parsed_document
        self.serialized_document = parser.serialised_document
        self.errors = []
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])

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
        self.check_intro_keywords()
        self.check_pictures()
        self.check_tables()
        self.check_appendices()
        self.check_bibliography()
        self.check_font_size()
        return {"valid": not bool(self.errors), "found": self.short_parsed_document(self.parsed_document),
                "errors": self.errors}

    def check_structure(self) -> None:
        structure = self.parsed_document["structure"]
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        required_sections = self.rules["structure_rules"].get("required_sections", {})

        # Соберём все главы (названия), как из нумерованных, так и ненумерованных
        numbered_chapters = [chapter["formatted_title"].lower() for chapter in structure.get("numbered_chapters", [])]
        unnumbered_chapters = [chapter["content"].strip().lower() for chapter in
                               structure.get("unnumbered_chapters", [])]
        all_chapters = numbered_chapters + unnumbered_chapters

        # Проверка обязательных глав
        for chapter in required_chapters:
            chapter_lower = chapter.lower()
            if not any(chapter_lower in ch for ch in all_chapters):
                self.add_error(f"Не найдена обязательная глава: '{chapter}'. Убедитесь, что она есть.")

        # Проверка разделов по главам
        sections = structure.get("sections", [])
        for chapter_num, required_sects in required_sections.items():
            # Собираем все названия разделов по конкретной главе
            chapter_sections = [
                s["content"].strip().lower()
                for s in sections
                if str(s.get("chapter_number")) == chapter_num
            ]

            for sect in required_sects:
                sect_lower = sect.lower()
                if not any(sect_lower in s for s in chapter_sections):
                    self.add_error(f"В главе {chapter_num} не найден обязательный раздел: '{sect}'. Убедитесь, что он есть.")

        suppress_errors = [
            "Не найдена обязательная глава: 'титульный лист'. Убедитесь, что она есть.",
            "В главе 1 не найден обязательный раздел: '1.1 раздел'. Убедитесь, что он есть.",
            "В главе 1 не найден обязательный раздел: '1.2 раздел'. Убедитесь, что он есть.",
            "В главе 2 не найден обязательный раздел: '2.1 раздел'. Убедитесь, что он есть.",
            "В главе 2 не найден обязательный раздел: '2.2 раздел'. Убедитесь, что он есть."
        ]

        for err in suppress_errors:
            if err in self.errors:
                self.errors.remove(err)

    def check_intro_keywords(self) -> None:
        introduction_keywords = self.rules["structure_rules"].get("introduction_keywords", [])
        bold_intro_words = self.parsed_document.get("bold_intro_words", [])

        for keyword in introduction_keywords:
            if not any(keyword in word for word in bold_intro_words):
                self.add_error(
                    f"Во введении не найдено ключевое слово или словосочетание выделенное жирным начертанием: '{keyword}'. Убедитесь, что оно у вас есть.")

    def check_pictures(self) -> None:
        pictures = self.parsed_document.get("pictures", {})
        references = pictures.get("references", [])
        captions = pictures.get("captions", [])

        ref_numbers = set(ref["ref_number"] for ref in references)
        caption_numbers = set(caption["figure_number"] for caption in captions)

        # Проверка на ссылки без подписей
        for num in ref_numbers:
            if num not in caption_numbers:
                self.add_error(
                    f"Есть ссылка на рисунок {num}, но подпись к нему не найдена. Проверьте оформление подписи.")

        # Проверка на подписи без ссылок
        for caption in captions:
            num = caption["figure_number"]
            if num not in ref_numbers:
                self.add_error(
                    f"Есть подпись к рисунку {num}, но ссылка на него в тексте отсутствует. Проверьте оформление ссылки.")

            # Проверка использования длинного тире
            if caption["dash"] != "—":
                self.add_error(
                    f"В подписи к рисунку {num} используется символ тире: '{caption['dash']}'. Следует использовать длинное тире '—' (U+2014)."
                )

    def check_tables(self) -> None:
        tables = self.parsed_document.get("tables", {})
        references = tables.get("references", [])
        captions = tables.get("captions", [])

        ref_numbers = set(ref["ref_number"] for ref in references)
        caption_numbers = set(caption["table_number"] for caption in captions)

        # Проверка на ссылки без подписей
        for num in ref_numbers:
            if num not in caption_numbers:
                self.add_error(
                    f"Есть ссылка на таблицу {num}, но подпись к ней не найдена. Проверьте оформление подписи.")

        # Проверка на подписи без ссылок
        for caption in captions:
            num = caption["table_number"]
            if num not in ref_numbers:
                self.add_error(
                    f"Есть подпись к таблице {num}, но ссылка на неё в тексте отсутствует. Проверьте оформление ссылки.")

    def check_bibliography(self) -> None:
        biblio = self.parsed_document.get("bibliography", {})
        references = biblio.get("references_in_text", [])
        bibliography_items = biblio.get("bibliography", [])

        ref_nums = set(int(re.sub(r"[^\d]", "", ref)) for ref in references if re.sub(r"[^\d]", "", ref).isdigit())
        biblio_nums = set(item["number"] for item in bibliography_items)

        # Ссылки без источников
        for num in ref_nums:
            if num not in biblio_nums:
                self.add_error(f"В тексте есть ссылка на источник [{num}], но в списке литературы он не найден.")

        # Источники без ссылок
        for num in biblio_nums:
            if num not in ref_nums:
                self.add_error(f"Источник [{num}] в списке литературы не используется в тексте.")

    def check_appendices(self) -> None:
        appendices = self.parsed_document.get("appendices", {})
        references = appendices.get("references", [])
        titles = appendices.get("titles", [])

        ref_letters = set(ref["ref_letter"] for ref in references)
        title_map = {title["appendix_letter"]: title for title in titles}

        # Ссылки без приложений
        for letter in ref_letters:
            if letter not in title_map:
                self.add_error(f"Есть ссылка на приложение {letter}, но соответствующее приложение не найдено.")

        # Приложения без ссылок
        for letter, title_info in title_map.items():
            if letter not in ref_letters:
                title_text = title_info.get("title", "").lower()
                if "ежедневные записи студента" not in title_text:
                    self.add_error(f"Приложение {letter} присутствует, но ссылка на него в тексте отсутствует.")

    def check_font_size(self):
        expected_size = str(self.rules["common_rules"]["font_size"])

        def recursive_check(paragraph, skip_subs_if_title=False):
            text = paragraph.get("text", "")
            annotations = paragraph.get("annotations", [])

            # Если текущий текст — "СОДЕРЖАНИЕ", не проверяем его вложенные подпараграфы
            skip_subs = text.strip().upper() == "СОДЕРЖАНИЕ"

            # Проверяем все size-аннотации
            for annotation in annotations:
                if annotation.get("name") == "size":
                    actual_size = str(annotation.get("value"))
                    if actual_size != expected_size:
                        self.add_error(
                            f"Неверный размер шрифта: '{text[:30]}...' (ожидается {expected_size}, найдено {actual_size})"
                        )

            # Рекурсивно проверяем вложенные подпараграфы, если это не СОДЕРЖАНИЕ
            if not skip_subs_if_title and not skip_subs:
                for sub in paragraph.get("subparagraphs", []):
                    recursive_check(sub)

        root = self.serialized_document["content"]["structure"]
        recursive_check(root)

    def short_parsed_document(self, parsed_document: dict) -> dict:
        def truncate(text, length=20):
            return text[:length] + ('...' if len(text) > length else '')

        result = {}

        # Структура
        if "structure" in parsed_document:
            struct = parsed_document["structure"]
            result["structure"] = {
                "numbered_chapters": [truncate(c.get("formatted_title", "")) for c in struct.get("numbered_chapters", [])],
                "unnumbered_chapters": [truncate(c.get("content", "")) for c in struct.get("unnumbered_chapters", [])]
            }

        # Введение: ключевые слова
        if "bold_intro_words" in parsed_document:
            result["bold_intro_words"] = [truncate(w) for w in parsed_document["bold_intro_words"]]

        # Списки
        if "lists" in parsed_document:
            lists = parsed_document["lists"]
            result["lists"] = {
                # key: [truncate(item) for item in items]
                # for key, items in lists.items()
            }

        # Рисунки
        if "pictures" in parsed_document:
            pictures = parsed_document.get("pictures", {})
            result["pictures"] = {
                "caption": [truncate(item.get("full_text", "")) for item in pictures.get("captions", [])],
                "ref": [item.get("ref_text", "") for item in pictures.get("references", [])]
            }

        # Таблицы
        if "tables" in parsed_document:
            tables = parsed_document["tables"]
            result["tables"] = {
                "caption": [truncate(item.get("raw_text", "")) for item in tables.get("captions", [])],
                "ref": [item.get("ref_text", "") for item in tables.get("references", [])]
            }

        # Приложения
        if "appendices" in parsed_document:
            appendices = parsed_document["appendices"]
            result["appendices"] = {
                "title": [truncate(item.get("raw_text", "")) for item in appendices.get("titles", [])],
                "ref": [item.get("ref_text", "") for item in appendices.get("references", [])]
            }

        # Библиография
        if "bibliography" in parsed_document:
            bib = parsed_document["bibliography"]
            result["bibliography"] = {
                "items": [truncate(item.get("content", ""), 25) for item in bib.get("bibliography", [])],
                "cite_keys": bib.get("references_in_text", [])
            }

        return result

