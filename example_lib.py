import json
from collections import Counter

from dedoc import DedocManager

file_path = "C:/Users/ALENA/PycharmProjects/AutoStandartControl/docs/diploma_lib.docx"
manager = DedocManager()  # создаем класс для универсальной обработки
result = manager.parse(file_path, {"document_type": "diploma"})  # обрабатываем файл

# print(result)  # <dedoc.data_structures.ParsedDocument>
serialised_doc = result.to_api_schema().model_dump()


def get_parts(annotations, needed_parts):
    found_parts = []  # Найденные разделы
    for annotation in annotations:
        if annotation["text"] in needed_parts:
            found_parts.append(annotation["text"])
    return found_parts


with open("rules/diploma_rules.json", "r", encoding="utf-8") as read_file:
    rules = json.load(read_file)
    required_chapters = rules["structure_rules"]["required_chapters"]

print(required_chapters)

found_parts = get_parts(serialised_doc["content"]["structure"]["subparagraphs"], required_chapters)

missing_parts = set(required_chapters) - set(found_parts)
duplicates = [part for part, count in Counter(found_parts).items() if count > 1]

# Вывод информации
print("\n📌 **Обязательные разделы:**")
print(", ".join(required_chapters))

print("\n✅ **Найденные разделы:**")
print(", ".join(found_parts) if found_parts else "❌ Нет найденных разделов")

if missing_parts:
    print("\n⚠️ **Отсутствуют разделы:**")
    print(", ".join(missing_parts))

if duplicates:
    print("\n🔁 **Повторяющиеся разделы:**")
    print(", ".join(duplicates))

#
#
# needed_parts = ['Введение']
#
# file_path = "/docs/diploma_lib.docx"
# manager = DedocManager()  # создаем класс для универсальной обработки
# result = manager.parse(file_path, {"document_type": "diploma"})  # обрабатываем файл
#
# print(result)  # <dedoc.data_structures.ParsedDocument>
# serialised_doc = result.to_api_schema().model_dump()  # сериализованное представление
#
# annotations = serialised_doc["content"]["structure"]["subparagraphs"]
# annotations = json.dumps(annotations, indent=2, ensure_ascii=False)
# #print(annotations)  # красивый вывод
#
# def get_parts(annotations, needed_parts):
#     result = []
#     for annotation in annotations:
#         if annotation["text"] in needed_parts:
#             result.append(annotation)
#     return result
#
# needed_parts = get_parts(serialised_doc["content"]["structure"]["subparagraphs"], needed_parts)
#
# print(json.dumps(needed_parts, indent=2, ensure_ascii=False))  # красивый вывод
#
#
# # Узнать размер шрифта и тип шрифта для заголовка Содержание
#
# def get_annotations_for_title(serialised_doc, title):
#     """
#     Возвращает аннотации для указанного заголовка.
#     """
#     annotations = serialised_doc["content"]["structure"]["subparagraphs"]
#     for annotation in annotations:
#         if annotation["text"] == title:
#             return annotation.get("annotations", [])
#     return []
#
# def extract_font_details(annotations):
#     """
#     Извлекает размер шрифта и тип шрифта из аннотаций.
#     """
#     font_size = None
#     font_style = None
#     for annotation in annotations:
#         if annotation["name"] == "size":
#             font_size = annotation["value"]
#         elif annotation["name"] == "style":
#             font_style = annotation["value"]
#     return font_size, font_style
#
# title = "Содержание"
#
# title1 = "Введение"
#
# annotations = get_annotations_for_title(serialised_doc, title)
#
# font_size, font_style = extract_font_details(annotations)
#
# print(f"Заголовок: {title}")
# print(f"Размер шрифта: {font_size}")
# print(f"Тип шрифта: {font_style}")
#
# annotations = get_annotations_for_title(serialised_doc, title1)
#
# font_size, font_style = extract_font_details(annotations)
#
# print(f"Заголовок: {title1}")
# print(f"Размер шрифта: {font_size}")
# print(f"Тип шрифта: {font_style}")
#
