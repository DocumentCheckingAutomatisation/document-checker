# Как использовать в командой строке:
#
# # Показать доступные типы
# python cli.py list-doc-types
#
# # Получить правила
# python cli.py get-rules diploma
#
# # Обновить правило
# python cli.py update-rule diploma common_rules.margin.top 20
#
# # Обновить для всех типов
# python cli.py update-rule-all common_rules.margin.top 20
#
# # Проверка DOCX
# python cli.py validate-docx C:\path\to\file.docx diploma
#
# # Проверка LaTeX
# python cli.py validate-latex C:\path\to\doc.tex C:\path\to\template.sty diploma


import argparse
import os
import tempfile
import json

from src.core.doc_type import DocType
from src.core.validator import OperationException
from src.logics.checkers.docx_checker import DocxChecker
from src.logics.checkers.latex_checker import LatexChecker
from src.logics.doc_service import DocService
from src.logics.rule_service import RuleService
from src.settings_manager import SettingsManager
from src.logics.logging import Logging

manager = SettingsManager()
manager.open("settings.json")
logger = Logging(manager)


def list_doc_options():
    doc_types = DocService.get_doc_types()
    print("Доступные типы документов:", doc_types)


def get_rules(doc_type):
    try:
        doc_type_enum = DocType[doc_type.upper()]
        rules = RuleService.load_rules(doc_type_enum)
        print(json.dumps(rules, indent=2, ensure_ascii=False))
    except KeyError:
        print(f"Неизвестный тип документа: {doc_type}")


def update_rule(doc_type, rule_key, new_value):
    try:
        doc_type_enum = DocType[doc_type.upper()]
        RuleService.update_rule(doc_type_enum, rule_key, new_value)
        print(f"Правило {rule_key} для {doc_type} успешно обновлено на {new_value}")
    except OperationException as e:
        print(f"Ошибка: {str(e)}")
    except Exception as e:
        print(f"Внутренняя ошибка: {str(e)}")


def update_rule_all(rule_key, new_value):
    updated = []
    errors = []
    for doc_type_enum in DocType:
        try:
            RuleService.update_rule(doc_type_enum, rule_key, new_value)
            updated.append(doc_type_enum.name.lower())
        except OperationException as e:
            errors.append(f"{doc_type_enum.name.lower()}: {str(e)}")
        except Exception:
            errors.append(f"{doc_type_enum.name.lower()}: Внутренняя ошибка")
    print("Обновление завершено.")
    print("Обновлены:", updated)
    if errors:
        print("Ошибки:", errors)


def validate_docx(file_path, doc_type):
    try:
        doc_type_enum = DocType[doc_type.upper()]
        checker = DocxChecker(file_path, doc_type)
        result = checker.check_document()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}")


def validate_latex(tex_path, sty_path, doc_type):
    try:
        doc_type_enum = DocType[doc_type.upper()]
        with open(tex_path, "rb") as tex_file, open(sty_path, "rb") as sty_file:
            checker = LatexChecker(tex_file, sty_file, doc_type)
            result = checker.check_document()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI для системы автоматического нормоконтроля")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-doc-types", help="Показать доступные типы документов")

    get_rules_parser = subparsers.add_parser("get-rules", help="Получить правила для типа документа")
    get_rules_parser.add_argument("doc_type", help="Тип документа (например: diploma, course_work, practice_report)")

    update_rule_parser = subparsers.add_parser("update-rule", help="Обновить правило")
    update_rule_parser.add_argument("doc_type")
    update_rule_parser.add_argument("rule_key")
    update_rule_parser.add_argument("new_value")

    update_all_parser = subparsers.add_parser("update-rule-all", help="Обновить правило для всех типов")
    update_all_parser.add_argument("rule_key")
    update_all_parser.add_argument("new_value")

    validate_docx_parser = subparsers.add_parser("validate-docx", help="Проверить .docx документ")
    validate_docx_parser.add_argument("file_path")
    validate_docx_parser.add_argument("doc_type")

    validate_latex_parser = subparsers.add_parser("validate-latex", help="Проверить LaTeX документ")
    validate_latex_parser.add_argument("tex_path")
    validate_latex_parser.add_argument("sty_path")
    validate_latex_parser.add_argument("doc_type")

    args = parser.parse_args()

    if args.command == "list-doc-types":
        list_doc_options()
    elif args.command == "get-rules":
        get_rules(args.doc_type)
    elif args.command == "update-rule":
        update_rule(args.doc_type, args.rule_key, args.new_value)
    elif args.command == "update-rule-all":
        update_rule_all(args.rule_key, args.new_value)
    elif args.command == "validate-docx":
        validate_docx(args.file_path, args.doc_type)
    elif args.command == "validate-latex":
        validate_latex(args.tex_path, args.sty_path, args.doc_type)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
