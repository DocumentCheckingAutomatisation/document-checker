from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.params import Path

from src.core.doc_type import DocType
from src.core.event_type import EventType
from src.core.validator import OperationException
from src.logics.checkers.docx_checker import DocxChecker
from src.logics.checkers.latex_checker import LatexChecker
from src.logics.doc_service import DocService
from src.logics.logging import Logging
from src.logics.observe_service import ObserveService
from src.logics.parsers.latex_parser import LatexParser
from src.logics.rule_service import RuleService
from src.settings_manager import SettingsManager

app = FastAPI()

manager = SettingsManager()
manager.open("settings.json")
logging = Logging(manager)


@app.get("/api/documents/options")
def docs_options():
    ObserveService.raise_event(EventType.LOG_DEBUG, "Запрос: /api/documents/options [GET]")
    doc_options = DocService.get_doc_types()
    ObserveService.raise_event(EventType.LOG_INFO, "Список доступных типов документов для проверки возвращен")
    return doc_options


@app.get("/api/rules/options")
def rules_options():
    ObserveService.raise_event(EventType.LOG_DEBUG, "Запрос: /api/rules/options [GET]")
    result = RuleService.get_rule_types()
    ObserveService.raise_event(EventType.LOG_INFO, "Список доступных типов правил проверки возвращен")
    return result


@app.get("/api/rules/{doc_type}")
def exact_rules(
        doc_type: str = Path(..., description="Тип документа",
                             enum=["diploma", "course_work", "practice_report"])
):
    ObserveService.raise_event(EventType.LOG_DEBUG, f"Запрос правил для типа документа: {doc_type} [GET]")
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")
    rules = RuleService.load_rules(doc_type_enum)
    ObserveService.raise_event(EventType.LOG_INFO, f"Правила для {doc_type} возвращены")
    return rules


@app.post("/api/rules/update")
def change_rules(doc_type: str, rule_key: str, new_value: str):
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    try:
        RuleService.update_rule(doc_type_enum, rule_key, new_value)
        ObserveService.raise_event(EventType.LOG_INFO, f"Правило {rule_key} для {doc_type} изменено на {new_value}")
        return {"message": f"Правило {rule_key} успешно обновлено"}
    except OperationException as e:
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.post("/api/documents/validate/single_file")
def validate_document_single_file(
        file: UploadFile = File(...),
        doc_type: str = Form(..., description="Тип документа (выберите из: diploma, course_work, practice_report)")
):
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension == "docx":
        checker = DocxChecker(file.file)
    elif file_extension == "tex":
        checker = LatexChecker(file.file)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла")

    validation_result = checker.check_document()
    return validation_result


@app.post("/api/documents/validate/latex")
def validate_document_latex(
        tex_file: UploadFile = File(...),
        sty_file: UploadFile = File(...),
        doc_type: str = Form(..., description="Тип документа (выберите из: diploma, course_work, practice_report)")
):
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    if not tex_file.filename.endswith(".tex"):
        raise HTTPException(status_code=400, detail=f"Ожидался .tex файл, но получен: {tex_file.filename}")
    if not sty_file.filename.endswith(".sty"):
        raise HTTPException(status_code=400, detail=f"Ожидался .sty файл, но получен: {sty_file.filename}")
    if tex_file.filename.endswith(".sty") or sty_file.filename.endswith(".tex"):
        raise HTTPException(status_code=400,
                            detail="Файлы перепутаны местами. Загрузите .tex как tex_file и .sty как sty_file")

    checker = LatexChecker(tex_file.file, sty_file.file, doc_type_enum)
    validation_result = checker.check_document()
    return validation_result
