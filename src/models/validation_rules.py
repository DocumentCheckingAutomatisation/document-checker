from src.core.abstract_model import AbstractModel
from src.models.rule import Rule
from src.core.doc_type import DocType

class ValidationRules(AbstractModel):
    def __init__(self, name=None, id=None, rules=None, doc_type=None):
        super().__init__(name, id)
        self.rules = rules or []
        self.doc_type: DocType = doc_type or ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rules": [rule.to_dict() for rule in self.rules],
            "doc_type": self.doc_type,
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.doc_type = data.get("doc_type", "")
        self.rules = [Rule().from_json(rule) for rule in data.get("rules", [])]

    def __eq__(self, other):
        return super().__eq__(
            other) and self.rules == other.rules and self.doc_type == other.doc_type

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.doc_type} - {self.rules}"