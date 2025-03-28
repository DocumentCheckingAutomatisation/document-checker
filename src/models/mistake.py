from src.core.abstract_model import AbstractModel
from src.core.validator import Validator
from src.models.rule import Rule


class Mistake(AbstractModel):
    __rule: Rule = None
    __message: str = ""

    def __init__(self):
        super().__init__()

    @property
    def rule(self):
        return self.__rule

    @rule.setter
    def rule(self, value):
        Validator.validate(value, Rule)
        self.__rule = value

    @property
    def message(self):
        return self.__message

    @message.setter
    def message(self, value):
        Validator.validate(value, str, 255)
        self.__message = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rule": self.rule.to_dict(),
            "message": self.message,
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.rule = Rule()
        self.rule.from_dict(data.get("rule", {}))

        self.message = data.get("message", "")

    def __eq__(self, other):
        return super().__eq__(other) and self.rule == other.rule and self.message == other.message

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.rule} - {self.message}"
