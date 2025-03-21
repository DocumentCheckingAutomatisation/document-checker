import json

from src.core.doc_type import DocType
from src.logics.parsers.latex_parser import LatexParser
from typing import List, Dict, Any
from src.logics.rule_service import RuleService


class LatexChecker:
    def __init__(self, tex_file, sty_file, doc_type: str):
        parser = LatexParser(tex_file)
        self.parsed_structure = parser.structure
        self.errors = parser.errors
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])

    def check_document(self) -> Dict[str, Any]:
        self.check_structure()
        return {"valid": not bool(self.errors), "errors": self.errors}

    def check_structure(self):
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        required_sections = self.rules["structure_rules"].get("required_sections", {})

        # Проверка глав
        all_chapters = [ch.lower() for ch in
                        self.parsed_structure["numbered_chapters"] + self.parsed_structure["unnumbered_chapters"]]

        for chapter in required_chapters:
            if not any(chapter in parsed_ch for parsed_ch in all_chapters):
                self.errors.append(f"Отсутствует обязательная глава: {chapter}")

        # Проверка разделов
        all_sections = [
            sec.lower() for sec in
            self.parsed_structure["numbered_sections"] + self.parsed_structure["unnumbered_sections"]
        ]
        for chapter, sections in required_sections.items():
            for section in sections:
                if not any(section in parsed_sec for parsed_sec in all_sections):
                    self.errors.append(f"В главе {chapter} отсутствует раздел: {section}")
        print(self.errors)

    def check_introduction_keywords(self):
        pass
