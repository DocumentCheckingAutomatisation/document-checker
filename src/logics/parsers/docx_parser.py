import re
from typing import Dict, Any, List, Optional
from docx import Document
from docx.shared import RGBColor


class DocxParser:
    def __init__(self, docx_file_path: str):
        self.docx_file_path = docx_file_path
        self.errors = []
        self.parsed_document = self.run_parse()

    def run_parse(self) -> Dict[str, Any]:
        doc = Document(self.docx_file_path)

        return {
            "structure": self.parse_structure(doc),
            "bold_intro_words": self.parse_intro(doc),
            "text": self.parse_text(doc),
            "lists": self.parse_lists(doc),
            "tables": self.parse_tables(doc),
            "pictures": self.parse_pictures(doc),
            "literature_links": self.parse_lit_links(doc)
        }

    def parse_structure(self, doc: Document) -> Dict[str, Any]:
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]
        numbered_chapters = []
        unnumbered_chapters = []
        numbered_sections = []
        unnumbered_sections = []
        common_text = []
        current_chapter = None

        for para in paragraphs:
            text = para.text.strip()

            # Заголовки глав и разделов
            if re.match(r"^\d+(\.\d+)?", text):  # Нумерованные
                if re.match(r"^\d+\s", text):  # Глава (например, "1 Глава")
                    numbered_chapters.append(self.extract_paragraph_info(para))
                    current_chapter = text.split()[0]
                elif re.match(r"^\d+\.\d+", text):  # Раздел (например, "1.1 Текст")
                    section_info = self.extract_paragraph_info(para)
                    section_info["chapter_number"] = current_chapter
                    numbered_sections.append(section_info)
            else:  # Ненумерованные
                if "выводы по главе" in text.lower():
                    section_info = self.extract_paragraph_info(para)
                    section_info["chapter_number"] = current_chapter
                    unnumbered_sections.append(section_info)
                if ...:
                    unnumbered_chapters.append(self.extract_paragraph_info(para))
                else:
                    common_text.append(self.extract_paragraph_info(para))

        return {
            "numbered_chapters": numbered_chapters,
            "unnumbered_chapters": unnumbered_chapters,
            "numbered_sections": numbered_sections,
            "unnumbered_sections": unnumbered_sections
        }

    def extract_paragraph_info(self, para) -> Dict[str, Any]:
        """ Извлекает информацию о стиле оформления абзаца """
        run = para.runs[0] if para.runs else None
        return {
            "content": para.text.strip(),
            "font_size": run.font.size.pt if run and run.font.size else None,
            "font_name": run.font.name if run else None,
            "font_color": self.get_font_color(run),
            "line_spacing": para.paragraph_format.line_spacing,
            "alignment": para.alignment if para.alignment else None,
            "left_indent": para.paragraph_format.left_indent.pt if para.paragraph_format.left_indent else None,
            "bold": run.bold if run else None,
            "uppercase": para.text.isupper(),
            "italic": run.italic if run else None,
            "underline": run.underline if run else None
        }

    def get_font_color(self, run) -> Optional[str]:
        if run and run.font.color and run.font.color.rgb:
            rgb: RGBColor = run.font.color.rgb
            return str(rgb)
        return None

    def parse_intro(self, doc: Document) -> List[str]:
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]
        inside_intro = False
        bold_words = []

        for para in paragraphs:
            text = para.text.strip().lower()
            if "введение" in text:
                inside_intro = True
                continue
            if inside_intro:
                if para.style.name.lower().startswith('heading'):
                    break  # Введение закончилось
                for run in para.runs:
                    if run.bold:
                        bold_words.append(run.text.strip().lower())

        return bold_words

    def parse_text(self, doc: Document) -> Dict[str, Any]:
        """ Парсинг обычного текста документа (не заголовков глав/разделов) """
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]
        text_runs = []

        for para in paragraphs:
            if not re.match(r"^\d+(\.\d+)?", para.text.strip()) and "выводы по главе" not in para.text.lower():
                for run in para.runs:
                    if run.text.strip():
                        text_runs.append(run)

        if not text_runs:
            return {}

        # Пробуем взять первый значащий run как эталон
        run = text_runs[0]

        return {
            "content": "\n".join([run.text for run in text_runs]),
            "font_size": run.font.size.pt if run.font.size else None,
            "font_name": run.font.name,
            "font_color": self.get_font_color(run),
            "line_spacing": paragraphs[0].paragraph_format.line_spacing,
            "alignment": paragraphs[0].alignment.name if paragraphs[0].alignment else None,
            "left_indent": paragraphs[0].paragraph_format.left_indent.pt if paragraphs[0].paragraph_format.left_indent else None,
            "bold": run.bold,
            "uppercase": [r.text.isupper() for r in text_runs],
            "italic": run.italic,
            "underline": run.underline
        }

    def parse_lists(self, doc: Document) -> List[Dict[str, Any]]:
        """ Парсинг списков: находим абзацы с bullets или нумерацией """
        lists = []
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]

        for para in paragraphs:
            if para.style.name.lower().startswith("list") or para.style.name.lower().startswith("bullet"):
                lists.append({
                    "list_item": para.text.strip(),
                    "font_size": para.runs[0].font.size.pt if para.runs and para.runs[0].font.size else None
                })

        return lists

    def parse_tables(self, doc: Document) -> List[Dict[str, Any]]:
        """ Парсинг таблиц: содержимое ячеек """
        tables = []

        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                table_data.append(row_data)
            tables.append({"table": table_data})

        return tables

    def parse_pictures(self, doc: Document) -> List[Dict[str, Any]]:
        """ Заглушка для парсинга картинок (без dedoc не получится обработать корректно) """
        pictures = []
        # Здесь можно позже интегрировать dedoc attachments для реального парсинга картинок
        return pictures

    def parse_lit_links(self, doc: Document) -> List[str]:
        """ Нахождение ссылок на литературу типа [1], [2] и т.д. """
        references = []
        paragraphs = [p for p in doc.paragraphs if p.text.strip()]
        for para in paragraphs:
            refs = re.findall(r"\[\d+\]", para.text)
            references.extend(refs)
        return list(set(references))



# import re
# from typing import Dict, Any, List
#
# from dedoc import DedocManager
# from docx import Document
#
#
# class DocxParser:
#     def __init__(self, docx_file_path):
#         self.docx_file_path = docx_file_path
#         self.errors = []
#         self.parsed_document = self.run_parse()
#
#     def run_parse(self) -> Dict[str, Any]:
#         # manager = DedocManager()
#         # result = manager.parse(self.docx_file_path, {"document_type": "diploma"})
#         # serialised_doc = result.to_api_schema().model_dump()
#         doc = Document(self.docx_file_path)
#
#         return {"structure": self.parse_structure(doc),
#                 "bold_intro_words": self.parse_intro(doc),
#                 "text": self.parse_text(doc),
#                 "lists": self.parse_lists(doc),
#                 "tables": self.parse_tables(doc),
#                 "pictures": self.parse_pictures(doc),
#                 "literature_links": self.parse_lit_links(doc)
#                 }
#
#     def parse_structure(self, doc: Document) -> Dict[str, Any]:
#         # парсинг нумерованных (1) и ненумерованных глав (содержание введение и тд), нумерованных (1.1) и ненумерованных разделов (выводы по главе)
#         # у разделов должно быть указано в какой они главе находятся
#         paragraphs = [p for p in doc.paragraphs if p.text.strip()]
#
#         return {
#             "numbered_chapters": {"content": ..., "font_size": ..., "font_name": ..., "font_color": ...,
#                                   "line_spacing": ..., "alignment": ..., "left_indent": ..., "bold": ...,
#                                   "uppercase": ..., "italic": ..., "underline": ...}, # добавляй еще если есть
#             "unnumbered_chapters": ...,
#             "numbered_sections": ...,
#             "unnumbered_sections": ...
#         }
#
#     def parse_intro(self, doc: Document) -> List[str]:
#         paragraphs = [p for p in doc.paragraphs if p.text.strip()]
#         inside_intro = False
#         bold_words = []
#
#         for para in paragraphs:
#             text = para.text.strip().lower()
#             if "введение" in text:
#                 inside_intro = True
#                 continue
#             if inside_intro:
#                 if para.style.name.lower().startswith('heading'):
#                     break  # Введение закончилось
#
#                 for run in para.runs:
#                     if run.bold:
#                         bold_words.append(run.text.lower())
#
#         return bold_words
#
#     def parse_text(self, doc: Document) -> Dict[str, Any]:
#         # парсинг кусков текста за исключением заголовков глав и разделов
#         return {
#             "content": ...,
#             "font_size": ...,
#             "font_name": ...,
#             "font_color": ...,
#             "line_spacing": ...,
#             "alignment": ...,
#             "left_indent": ...,
#             "bold": ...,
#             "uppercase": [run.text.isupper() for p in doc.paragraphs for run in p.runs],
#             "italic": ...,
#             "underline": ...
#         }
#
#     def parse_lists(self, serialised_doc):
#         # парсинг списков: вводное предложение (то есть 1 предложение до элементов списка) и сами элементы списка
#         pass
#
#     def parse_tables(self, serialised_doc):
#         pass
#
#     def parse_pictures(self, serialised_doc):
#         # парсинг рисунков их подписей и ссылок на них и свойств (отступы размеры шрифта и тд)
#         pass
#
#     def parse_lit_links(self, serialised_doc):
#         # нахождение ссылки в формате [1] на элемент в списке использованных источников и самого элемента
#         pass


#
# from typing import Dict, Any, List
#
# from dedoc import DedocManager
#
#
# class DocxParser:
#     def __init__(self, docx_file_path):
#         self.docx_file_path = docx_file_path
#         self.errors = []
#         self.parsed_document = self.run_parse()
#
#     def run_parse(self) -> Dict[str, Any]:
#         manager = DedocManager()
#         result = manager.parse(self.docx_file_path, {"document_type": "diploma"})
#         serialised_doc = result.to_api_schema().model_dump()
#
#         return {"structure": self.parse_structure(serialised_doc),
#                 "fonts": self.parse_font_details(serialised_doc)
#                 }
#
#     def parse_structure(self, serialised_doc: Dict[str, Any]) -> Dict[str, Any]:
#         chapters = serialised_doc["content"]["structure"]
#         return {"found_chapters": chapters}
#
#     def parse_font_details(self, serialised_doc: Dict[str, Any]) -> Dict[str, Any]:
#         fonts = {}
#         for annotation in serialised_doc["content"]["structure"]["subparagraphs"]:
#             title = annotation["text"]
#             font_size, font_bold = self.extract_font_details(annotation.get("annotations", []))
#             fonts[title] = {"size": font_size, "bold": font_bold}
#         return fonts
#
#     @staticmethod
#     def extract_font_details(annotations: List[Dict[str, Any]]):
#         font_size = None
#         font_bold = False
#         for annotation in annotations:
#             if annotation["name"] == "size":
#                 font_size = annotation["value"]
#             elif annotation["name"] == "bold":
#                 font_bold = True
#         return font_size, font_bold
