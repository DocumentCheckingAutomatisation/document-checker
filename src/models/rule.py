from src.core import rule_type
from src.core.abstract_model import AbstractModel


class Rule(AbstractModel):
    def __init__(self, name=None, id=None, attribute=None, rule_type=None, condition=None):
        super().__init__(name, id)
        self.attribute = attribute or ""
        self.rule_type: rule_type = rule_type or ""
        self.condition = condition or ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "attribute": self.attribute,
            "rule_type": self.rule_type,
            "condition": self.condition,
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.rule_type = data.get("rule_type", "")
        self.attribute = data.get("attribute", "")
        self.condition = data.get("condition", "")

    def __eq__(self, other):
        return super().__eq__(
            other) and self.condition == other.condition and self.action == other.action and self.rule_type == other.rule_type

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.rule_type} - {self.attribute} - {self.condition}"
