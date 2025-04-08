import json
from pathlib import Path

from src.core.abstract_logic import AbstractLogic
from src.core.doc_type import DocType
from src.core.event_type import EventType
from src.core.rule_type import RuleType
from src.logics.observe_service import ObserveService
from src.core.validator import OperationException


class RuleService(AbstractLogic):
    RULES_PATH = Path(__file__).resolve().parent.parent.parent / "rules"

    def __init__(self):
        ObserveService.append(self)

    @classmethod
    def get_rules_path(cls, doc_type: DocType) -> str:
        """Возвращает путь к файлу с правилами для указанного типа документа."""
        return f"{cls.RULES_PATH}/{doc_type.name.lower()}_rules.json"

    @classmethod
    def load_rules(cls, doc_type: DocType):
        file_path = cls.get_rules_path(doc_type)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка загрузки правил: {e}")
            return {}

    @staticmethod
    def get_rule_types():
        return [{"name": rule.name, "value": rule.value} for rule in RuleType]

    @classmethod
    def save_rules(cls, doc_type: DocType, rules_data: dict):
        file_path = cls.get_rules_path(doc_type)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(rules_data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка при сохранении правил: {e}")
            return False

    @classmethod
    def update_rule(cls, doc_type: DocType, rule_path: str, new_value):
        rules_data = cls.load_rules(doc_type)

        keys = rule_path.split(".")  # Разбиваем путь по точкам
        current = rules_data

        for key in keys[:-1]:  # Проходим по всем ключам, кроме последнего
            if key in current:
                current = current[key]
            else:
                raise OperationException(f"Раздел {key} не найден.")

        last_key = keys[-1]
        if last_key not in current:
            raise OperationException(f"Правило {last_key} не найдено.")

        try:
            if isinstance(current[last_key], bool):
                new_value = new_value.lower() == "true"
            elif isinstance(current[last_key], int):
                new_value = int(new_value)
            elif isinstance(current[last_key], float):
                new_value = float(new_value)
            elif isinstance(current[last_key], list) and isinstance(new_value, str):
                new_value = json.loads(new_value)  # проверка корректности списка
        except (ValueError, json.JSONDecodeError) as e:
            raise OperationException(f"Ошибка приведения типов для {rule_path}: {e}")
        current[last_key] = new_value

        if not cls.save_rules(doc_type, rules_data):
            raise OperationException("Ошибка при сохранении правил.")

        return True

    def set_exception(self, ex: Exception):
        super().set_exception(ex)

    def handle_event(self, event_type: EventType, params):
        super().handle_event(event_type, params)
