from src. core.abstract_model import AbstractModel
from src.core.doc_type import DocType
from src.models.validation_result import ValidationResult

class Document(AbstractModel):
    def __init__(self, name=None, id=None, doc_type=None, result=None):
        super().__init__(name, id)
        self.doc_type: DocType = doc_type or DocType()
        self.result: ValidationResult = result or ValidationResult()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "doc_type": self.doc_type.to_dict(),
            "result": self.result.to_dict(),
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.doc_type = DocType().from_json(data.get("doc_type", {}))
        self.result = ValidationResult().from_json(data.get("result", {}))

    def __eq__(self, other):
        return super().__eq__(other) and self.doc_type == other.doc_type and self.result == other.result

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.doc_type} - {self.result}"