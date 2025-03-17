from src.core.abstract_model import AbstractModel
from src.core.doc_type import DocType
from src.core.validator import Validator
from src.models.validation_result import ValidationResult


class Document(AbstractModel):
    """Модель документа"""
    __content = None
    __doc_type: DocType = None
    __result: ValidationResult = None

    def __init__(self):
        super().__init__()

    @property
    def doc_type(self):
        return self.__doc_type

    @doc_type.setter
    def doc_type(self, value):
        Validator.validate(value, DocType)
        self.__doc_type = value

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        Validator.validate(value, ValidationResult)
        self.__result = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "doc_type": self.doc_type.name if self.doc_type else None,
            "result": self.result.to_dict(),
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.doc_type = DocType[data.get("doc_type")] if data.get("doc_type") else None

        self.result = ValidationResult()
        self.result.from_dict(data.get("result", {}))

    def __eq__(self, other):
        return super().__eq__(other) and self.doc_type == other.doc_type and self.result == other.result

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.doc_type} - {self.result}"
