from src.core.abstract_model import AbstractModel
from src.core.doc_type import DocType
from src.core.validator import Validator
from src.models.rule import Rule


class ValidationRules(AbstractModel):
    __rules: list = []
    __doc_type: DocType = None

    def __init__(self):
        super().__init__()

    @property
    def rules(self):
        return self.__rules

    @rules.setter
    def rules(self, value):
        Validator.validate(value, list)
        self.__rules = value

    @property
    def doc_type(self):
        return self.__doc_type

    @doc_type.setter
    def doc_type(self, value):
        Validator.validate(value, DocType)
        self.__doc_type = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rules": [rule.to_dict() for rule in self.rules],
            "doc_type": self.doc_type.name if self.doc_type else None,
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.doc_type = DocType[data.get("doc_type")] if data.get("doc_type") else None
        self.rules = [Rule().from_dict(rule) for rule in data.get("rules", [])]

    def __eq__(self, other):
        return super().__eq__(
            other) and self.rules == other.rules and self.doc_type == other.doc_type

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.doc_type} - {self.rules}"
