from src.core.abstract_model import AbstractModel
from src.core.rule_type import RuleType
from src.core.validator import Validator


class Rule(AbstractModel):
    __attribute: str = ""
    __rule_type: RuleType = None
    __condition: str = ""

    def __init__(self):
        super().__init__()

    @property
    def attribute(self):
        return self.__attribute

    @attribute.setter
    def attribute(self, value):
        Validator.validate(value, str, 255)
        self.__attribute = value

    @property
    def rule_type(self):
        return self.__rule_type

    @rule_type.setter
    def rule_type(self, value):
        Validator.validate(value, RuleType)
        self.__rule_type = value

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, value):
        Validator.validate(value, str, 255)
        self.__condition = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "attribute": self.attribute,
            "rule_type": self.rule_type.name if self.rule_type else None,
            "condition": self.condition,
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.rule_type = RuleType[data.get("rule_type")] if data.get("rule_type") else None
        self.attribute = data.get("attribute", "")
        self.condition = data.get("condition", "")

    def __eq__(self, other):
        return super().__eq__(
            other) and self.attribute == other.attribute and self.rule_type == other.rule_type and self.condition == other.condition

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.rule_type} - {self.attribute} - {self.condition}"
