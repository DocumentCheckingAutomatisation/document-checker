import re
from typing import Dict, Any


class LatexParser:
    def __init__(self, tex_file):
        self.tex_content = tex_file.read().decode("utf-8")
        self.structure = self.parse_structure()

    def parse_structure(self) -> Dict[str, Any]:
        numbered_chapters = re.findall(r'\\chapter\{(.+?)\}', self.tex_content)
        unnumbered_chapters = re.findall(r'\\chapter\*\{(.+?)\}', self.tex_content)

        sections = re.findall(r'\\section\{(.+?)\}', self.tex_content)
        parsed_structure = {"numbered_chapters": numbered_chapters, "unnumbered_chapters": unnumbered_chapters,
                            "sections": sections}
        return parsed_structure
