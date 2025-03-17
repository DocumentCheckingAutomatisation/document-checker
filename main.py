import json
import os

import connexion
from flask import Response
from flask import request

from src.core.doc_type import DocType
from src.core.event_type import EventType
from src.core.validator import OperationException
from src.logics.checkers.docx_checker import DocxChecker
from src.logics.checkers.latex_checker import LatexChecker
from src.logics.doc_service import DocService
from src.logics.checkers.doc_validator import DocumentValidator
from src.logics.logging import Logging
from src.logics.observe_service import ObserveService
from src.logics.rule_service import RuleService
from src.settings_manager import SettingsManager

app = connexion.FlaskApp(__name__)

manager = SettingsManager()
manager.open("settings.json")
logging = Logging(manager)


@app.route("/api/documents/options", methods=["GET"])
def docs_for_validation_options():
    ObserveService.raise_event(EventType.LOG_DEBUG, params="Запрос: /api/documents/options [GET]")
    doc_options = DocService.get_doc_types()
    ObserveService.raise_event(EventType.LOG_INFO, params="Список доступных типов документов для проверки возвращен")
    return doc_options


@app.route("/api/rules/options", methods=["GET"])
def rules_options():
    ObserveService.raise_event(EventType.LOG_DEBUG, params="Запрос: /api/rules/options [GET]")
    result = RuleService.get_rule_types()
    ObserveService.raise_event(EventType.LOG_INFO, params="Список доступных типов правил проверки возвращен")
    return result


@app.route("/api/rules/<doc_type>", methods=["GET"])
def exact_rules(doc_type):
    ObserveService.raise_event(EventType.LOG_DEBUG, params=f"Запрос правил для типа документа: {doc_type} [GET]")
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        return Response(f"Неизвестный тип документа: {doc_type}", status=400)
    rules = RuleService.get_rules_for_doc(doc_type_enum)
    ObserveService.raise_event(EventType.LOG_INFO, params=f"Правила для {doc_type} возвращены")
    return rules


@app.route("/api/rules/update", methods=["POST"])
def change_rules():
    data = request.get_json()
    if not data:
        return Response("Нет данных в запросе", status=400)

    doc_type_str = data.get("doc_type")
    rule_key = data.get("rule_key")
    new_value = data.get("new_value")  # Для списка: "[\"Титульный лист\",\"Содержание\",\"Введение\",\"1\",\"2\",\"Заключение\",\"Список использованных источников\",\"Приложение\"]"

    if not doc_type_str or not rule_key or not new_value:
        return Response("Необходимо передать 'doc_type', 'rule_key' и 'new_value'", status=400)

    try:
        doc_type_enum = DocType[doc_type_str.upper()]
    except KeyError:
        return Response(f"Неизвестный тип документа: {doc_type_str}", status=400)

    try:
        RuleService.update_rule(doc_type_enum, rule_key, new_value)
        ObserveService.raise_event(EventType.LOG_INFO,
                                   params=f"Правило {rule_key} для {doc_type_str} изменено на {new_value}")
        return Response(f"Правило {rule_key} успешно обновлено на {new_value}", status=200)
    except OperationException as e:
        return Response(f"Ошибка: {str(e)}", status=400)
    except Exception as e:
        return Response(f"Внутренняя ошибка сервера: {str(e)}", status=500)

@app.route("/api/documents/validate", methods=["POST"])
def validate_document():
    data = request.get_json()
    if not data or "document" not in data:
        return Response("Отсутствует документ в запросе", status=400)

    document = data["document"]
    validator = DocumentValidator(document)

    if not validator.validate():
        return Response("Документ недействителен или пуст", status=400)

    with open("rules/diploma_rules.json", "r", encoding="utf-8") as file:
        rules = json.load(file)
        required_chapters = rules["structure_rules"]["required_chapters"]

    found_parts = validator.get_parts(required_chapters)
    missing_parts = set(required_chapters) - set([p["text"] for p in found_parts])
    duplicates = [part["text"] for part in found_parts if found_parts.count(part) > 1]

    response_data = {
        "required_chapters": required_chapters,
        "found_chapters": [p["text"] for p in found_parts],
        "missing_chapters": list(missing_parts),
        "duplicate_chapters": duplicates
    }

    return response_data, 200


@app.route("/api/documents/check", methods=["POST"])
def check_document():
    if "file" not in request.files or "doc_type" not in request.form:
        return Response("Файл и тип документа обязательны", status=400)

    file = request.files["file"]
    doc_type = request.form["doc_type"].upper()

    try:
        doc_type_enum = DocType[doc_type]
    except KeyError:
        return Response(f"Неизвестный тип документа: {doc_type}", status=400)

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension == ".docx":
        checker = DocxChecker(file)
    elif file_extension == ".tex":
        checker = LatexChecker(file)
    else:
        return Response("Неподдерживаемый формат файла", status=400)

    validation_result = checker.check_document()
    return validation_result, 200


if __name__ == '__main__':
    ObserveService.raise_event(EventType.LOG_INFO, params="Запуск API")
    app.add_api("swagger.yaml")
    app.run(port=8080)
