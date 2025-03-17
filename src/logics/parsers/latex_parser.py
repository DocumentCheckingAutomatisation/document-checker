import re
from src.models.document import Document
from src.core.doc_type import DocType


class LatexParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = ""
        self.structure = {
            "chapters": [],
            "sections": [],
            "subsections": []
        }

    def parse(self):
        """Считывает содержимое файла и извлекает структуру документа."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            self.content = file.read()

        self.structure["chapters"] = re.findall(r"\\chapter{(.*?)}", self.content)
        self.structure["sections"] = re.findall(r"\\section{(.*?)}", self.content)
        self.structure["subsections"] = re.findall(r"\\subsection{(.*?)}", self.content)

    def to_document(self):
        """Конвертирует спарсенные данные в объект Document."""
        doc = Document()
        doc.name = "Parsed LaTeX Document"
        doc.doc_type = DocType.DIPLOMA  # Можно определить по контексту
        doc.result = None  # Проверки пока не проводим
        doc._Document__content = self.structure  # Сохраняем структуру
        return doc
