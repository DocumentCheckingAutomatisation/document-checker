from typing import Dict, Any

from src.core.doc_type import DocType
from src.logics.parsers.docx_parser import DocxParser
from src.logics.rule_service import RuleService


class DocxChecker:
    def __init__(self, docx_file_path, doc_type: str):
        parser = DocxParser(docx_file_path)
        self.parsed_document = parser.parsed_document
        self.errors = parser.errors
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])

    def check_document(self) -> Dict[str, Any]:
        self.check_structure()
        self.check_font_size()
        return {"valid": not bool(self.errors), "errors": self.errors}

    @staticmethod
    def get_parts(annotations, needed_parts):
        found_parts = []
        for annotation in annotations:
            if "заключение" in annotation["text"].lower():
                found_parts.append("заключение")
            if "глава 1" in annotation["text"].lower():
                found_parts.append("1 глава")
            if "глава 2" in annotation["text"].lower():
                found_parts.append("2 глава")
            if annotation["text"].lower() in needed_parts:
                found_parts.append(annotation["text"].lower())
        return found_parts

    def check_structure(self):
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        title_keywords = self.rules["design_rules"].get("title", {}).get("doc_type", [])

        annotations = self.parsed_document["structure"]["found_chapters"]["subparagraphs"]
        document_text = self.parsed_document["structure"]["found_chapters"].get("text", "").lower()

        found_parts = self.get_parts(annotations, required_chapters)

        if any(keyword in document_text for keyword in title_keywords):
            found_parts.append("титульный лист")

        missing_parts = set(required_chapters) - set(found_parts)
        duplicate_parts = [part for part in found_parts if found_parts.count(part) > 1]

        if missing_parts:
            self.errors.append(f"Отсутствует обязательная глава: {', '.join(missing_parts)}")
        if duplicate_parts:
            self.errors.append(f"Повторяющиеся главы: {', '.join(set(duplicate_parts))}")

    def check_font_size(self):
        expected_size = self.rules["design_rules"]["chapter"]["font_size"]
        expected_bold = self.rules["design_rules"]["chapter"]["bold"]
        found_fonts = self.parsed_document["fonts"]

        for title, font_details in found_fonts.items():
            if title == '' and font_details['size'] is None:
                continue
            else:
                print(title, font_details['bold'], expected_bold)
                if expected_size and font_details["size"] != expected_size:
                    self.errors.append(
                        f"Неверный размер шрифта в заголовке '{title}': {font_details['size']} (ожидалось {expected_size})")
                if expected_bold and font_details["bold"] != expected_bold:
                    self.errors.append(
                        f"Неверный стиль шрифта в заголовке '{title}': {font_details['bold']} (ожидалось {expected_bold})")
