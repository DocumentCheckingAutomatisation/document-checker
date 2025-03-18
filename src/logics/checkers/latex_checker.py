from src.models.document import Document


class LatexChecker():
    def __init__(self, tex_file, sty_file):
        self.tex_file = tex_file
        self.sty_file = sty_file

    def check_document(self):
        try:
            document = Document(self.file)
        except Exception as e:
            return f"Ошибка при открытии документа: {str(e)}"

        if not document.paragraphs:
            return "Документ пуст"

        return "Документ успешно проверен"