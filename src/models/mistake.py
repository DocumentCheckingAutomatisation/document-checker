from src.core.abstract_model import AbstractModel
from src.models.rule import Rule

class Mistake(AbstractModel):
    def __init__(self, name=None, id=None, rule=None, message=None):
        super().__init__(name, id)
        self.rule: Rule = rule or Rule()
        self.message: str = message or ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rule": self.rule.to_dict(),
            "message": self.message,
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.rule = Rule().from_json(data.get("rule", {}))
        self.message = data.get("message", "")

    def __eq__(self, other):
        return super().__eq__(other) and self.rule == other.rule and self.message == other.message

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.rule} - {self.message}"


