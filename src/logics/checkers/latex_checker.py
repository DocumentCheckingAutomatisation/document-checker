import json

from src.core.doc_type import DocType
from src.logics.parsers.latex_parser import LatexParser
from typing import List, Dict, Any
from src.logics.rule_service import RuleService


class LatexChecker():
    def __init__(self, tex_file, sty_file, doc_type: str):
        self.parsed_structure = LatexParser(tex_file).structure
        self.rules = RuleService.load_rules(DocType[doc_type.upper()])
        self.errors = []

    def check_document(self) -> Dict[str, Any]:
        self.check_structure()
        return {"valid": not bool(self.errors), "errors": self.errors}

    def check_structure(self):
        required_chapters = self.rules["structure_rules"].get("required_chapters", [])
        required_sections = self.rules["structure_rules"].get("required_sections", {})

        # Проверка глав (нумерованных и ненумерованных)
        all_chapters = [ch.lower() for ch in self.parsed_structure["numbered_chapters"] + self.parsed_structure["unnumbered_chapters"]]

        for chapter in required_chapters:
            if not any(chapter in parsed_ch for parsed_ch in all_chapters):
                self.errors.append(f"Отсутствует обязательная глава: {chapter}")

        # Проверка разделов в главах
        for chapter, sections in required_sections.items():
            for section in sections:
                if not any(section in parsed_sec for parsed_sec in self.parsed_structure["sections"]):
                    self.errors.append(f"В главе {chapter} отсутствует раздел: {section}")

        print(self.errors)



    # def check_document(self):
    #     errors = []
    #     structure_rules = self.rules.get("structure_rules", {})
    #
    #     required_chapters = structure_rules.get("required_chapters", [])
    #     for chapter in required_chapters:
    #         if chapter not in self.parsed_structure.chapters:
    #             errors.append(f"Отсутствует обязательный раздел: {chapter}")
    #
    #     required_sections = structure_rules.get("required_sections", {})
    #     for chapter, sections in required_sections.items():
    #         if chapter in self.parsed_structure.sections:
    #             for section in sections:
    #                 if section not in self.parsed_structure.sections[chapter]:
    #                     errors.append(f"В главе {chapter} отсутствует обязательный раздел: {section}")
    #
    #     return {"errors": errors}