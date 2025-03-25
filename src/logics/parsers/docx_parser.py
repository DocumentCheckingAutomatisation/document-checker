from typing import Dict, Any, List

from dedoc import DedocManager


class DocxParser:
    def __init__(self, docx_file_path):
        self.docx_file_path = docx_file_path
        self.errors = []
        self.parsed_document = self.run_parse()

    def run_parse(self) -> Dict[str, Any]:
        manager = DedocManager()
        result = manager.parse(self.docx_file_path, {"document_type": "diploma"})
        serialised_doc = result.to_api_schema().model_dump()

        return {"structure": self.parse_structure(serialised_doc),
                "fonts": self.parse_font_details(serialised_doc)
                }

    def parse_structure(self, serialised_doc: Dict[str, Any]) -> Dict[str, Any]:
        chapters = serialised_doc["content"]["structure"]
        return {"found_chapters": chapters}

    def parse_font_details(self, serialised_doc: Dict[str, Any]) -> Dict[str, Any]:
        fonts = {}
        for annotation in serialised_doc["content"]["structure"]["subparagraphs"]:
            title = annotation["text"]
            font_size, font_bold = self.extract_font_details(annotation.get("annotations", []))
            fonts[title] = {"size": font_size, "bold": font_bold}
        return fonts

    @staticmethod
    def extract_font_details(annotations: List[Dict[str, Any]]):
        font_size = None
        font_bold = False
        for annotation in annotations:
            if annotation["name"] == "size":
                font_size = annotation["value"]
            elif annotation["name"] == "bold":
                font_bold = True
        return font_size, font_bold
