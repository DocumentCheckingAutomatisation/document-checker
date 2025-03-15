from src.core.abstract_logic import AbstractLogic


class DocumentValidator(AbstractLogic):
    def __init__(self, document):
        self.document = document

    def validate(self):
        if not self.document:
            return False

        return True

    def get_parts(self, needed_parts):
        result = []
        for annotation in self.document:
            if annotation["text"] in needed_parts:
                result.append(annotation)
        return result

    def get_annotations_for_title(self, title):
        annotations = self.document
        for annotation in annotations:
            if annotation["text"] == title:
                return annotation.get("annotations", [])
        return []

    def extract_font_details(self, annotations):
        font_size = None
        font_style = None
        for annotation in annotations:
            if annotation["name"] == "size":
                font_size = annotation["value"]
            elif annotation["name"] == "style":
                font_style = annotation["value"]
        return font_size, font_style

    def get_font_details(self, title):
        annotations = self.get_annotations_for_title(title)
        return self.extract_font_details(annotations)

    def get_font_details_for_title(self, title):
        font_size, font_style = self.get_font_details(title)
        return f"Заголовок: {title}\nРазмер шрифта: {font_size}\nТип шрифта: {font_style}"

    def get_font_details_for_titles(self, titles):
        result = []
        for title in titles:
            result.append(self.get_font_details_for_title(title))
        return result

    def handle_event(self, event_type, params):
        pass

    def set_exception(self, ex: Exception):
        pass





