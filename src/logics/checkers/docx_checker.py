from src.logics.parsers.docx_parser import DocxParser
from src.models.document import Document


class DocxChecker:
    def __init__(self, file):
        parser = DocxParser()
        self.file = file

    def check_document(self):
        try:
            document = Document(self.file)
        except Exception as e:
            return f"Ошибка при открытии документа: {str(e)}"

        if not document.paragraphs:
            return "Документ пуст"

        return "Документ успешно проверен"