import os
import tempfile

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
        ObserveService.raise_event(EventType.LOG_ERROR, f"Неизвестный тип документа: {doc_type}")
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    rules = RuleService.load_rules(doc_type_enum)
    ObserveService.raise_event(EventType.LOG_INFO, f"Правила для {doc_type} возвращены")
    return rules


@app.post("/api/rules/update")
def change_rules(doc_type: str, rule_key: str, new_value: str):
    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        ObserveService.raise_event(EventType.LOG_ERROR,
                                   f"Попытка обновления правила для неизвестного типа документа: {doc_type}")
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    try:
        RuleService.update_rule(doc_type_enum, rule_key, new_value)
        ObserveService.raise_event(EventType.LOG_INFO, f"Правило {rule_key} для {doc_type} изменено на {new_value}")
        return {"message": f"Правило {rule_key} успешно обновлено"}
    except OperationException as e:
        ObserveService.raise_event(EventType.LOG_ERROR, f"Ошибка при обновлении правила {rule_key}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка: {str(e)}")
    except Exception as e:
        ObserveService.raise_event(EventType.LOG_ERROR,
                                   f"Внутренняя ошибка сервера при обновлении правила {rule_key}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@app.post("/api/rules/update/all")
def change_rule_for_all(rule_key: str, new_value: str):
    ObserveService.raise_event(EventType.LOG_DEBUG,
                               f"Запрос на изменение правила {rule_key} для всех типов документов [POST]")

    updated_docs = []
    errors = []

    for doc_type_enum in DocType:
        try:
            RuleService.update_rule(doc_type_enum, rule_key, new_value)
            updated_docs.append(doc_type_enum.name.lower())
            ObserveService.raise_event(EventType.LOG_INFO,
                                       f"Правило {rule_key} для {doc_type_enum.name.lower()} обновлено на {new_value}")
        except OperationException as e:
            errors.append(f"{doc_type_enum.name.lower()}: {str(e)}")
            ObserveService.raise_event(EventType.LOG_ERROR,
                                       f"Ошибка при обновлении {rule_key} для {doc_type_enum.name.lower()}: {str(e)}")
        except Exception as e:
            errors.append(f"{doc_type_enum.name.lower()}: Внутренняя ошибка")
            ObserveService.raise_event(EventType.LOG_ERROR,
                                       f"Внутренняя ошибка сервера при обновлении {rule_key} для {doc_type_enum.name.lower()}: {str(e)}")

    if errors:
        return {"message": "Некоторые обновления прошли с ошибками", "updated": updated_docs, "errors": errors}
    return {"message": f"Правило {rule_key} успешно обновлено для всех типов документов", "updated": updated_docs}


@app.post("/api/documents/validate/latex")
def validate_document_latex(
        tex_file: UploadFile = File(...),
        sty_file: UploadFile = File(...),
        doc_type: str = Form(..., description="Тип документа (выберите из: diploma, course_work, practice_report)")
):
    ObserveService.raise_event(EventType.LOG_DEBUG,
                               f"Загрузка файлов {tex_file.filename} и {sty_file.filename} для проверки [POST]")

    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        ObserveService.raise_event(EventType.LOG_ERROR, f"Неизвестный тип документа: {doc_type}")
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    if not tex_file.filename.endswith(".tex"):
        ObserveService.raise_event(EventType.LOG_ERROR, f"Ошибка: ожидался .tex файл, но получен {tex_file.filename}")
        raise HTTPException(status_code=400, detail=f"Ожидался .tex файл, но получен: {tex_file.filename}")
    if not sty_file.filename.endswith(".sty"):
        ObserveService.raise_event(EventType.LOG_ERROR, f"Ошибка: ожидался .sty файл, но получен {sty_file.filename}")
        raise HTTPException(status_code=400, detail=f"Ожидался .sty файл, но получен: {sty_file.filename}")
    if tex_file.filename.endswith(".sty") or sty_file.filename.endswith(".tex"):
        ObserveService.raise_event(EventType.LOG_ERROR, "Ошибка: файлы перепутаны местами")
        raise HTTPException(status_code=400,
                            detail="Файлы перепутаны местами. Загрузите .tex как tex_file и .sty как sty_file")

    checker = LatexChecker(tex_file.file, sty_file.file, doc_type_enum)
    validation_result = checker.check_document()
    ObserveService.raise_event(EventType.LOG_INFO, f"Файлы {tex_file.filename} и {sty_file.filename} успешно проверены")
    return validation_result

@app.post("/api/documents/validate/single_file")
def validate_document_single_file(
        file: UploadFile = File(...),
        doc_type: str = Form(..., description="Тип документа (выберите из: diploma, course_work, practice_report)")
):
    ObserveService.raise_event(EventType.LOG_DEBUG, f"Загрузка файла {file.filename} для проверки [POST]")

    try:
        doc_type_enum = DocType[doc_type.upper()]
    except KeyError:
        ObserveService.raise_event(EventType.LOG_ERROR, f"Неизвестный тип документа: {doc_type}")
        raise HTTPException(status_code=400, detail=f"Неизвестный тип документа: {doc_type}")

    # Проверяем, что файл имеет расширение .docx
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension != "docx":
        ObserveService.raise_event(EventType.LOG_ERROR, f"Неподдерживаемый формат файла: {file.filename}")
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат файла. Ожидается .docx")

    # Сохраняем файл на диск
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        temp_file.write(file.file.read())  # Сохраняем содержимое файла
        temp_file_path = temp_file.name  # Получаем путь к сохраненному файлу

    # Инициализация чекера для .docx файла с путем
    checker = DocxChecker(temp_file_path, doc_type_enum)

    validation_result = checker.check_document()
    ObserveService.raise_event(EventType.LOG_INFO, f"Файл {file.filename} успешно проверен")

    # После проверки можно удалить временный файл
    os.remove(temp_file_path)

    return validation_result
