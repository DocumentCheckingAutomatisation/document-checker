from src.core.abstract_model import AbstractModel
from src.core.validator import Validator
from src.models.mistake import Mistake


class Recommendation(AbstractModel):
    __mistake: Mistake = None
    __message: str = ""

    def __init__(self):
        super().__init__()

    @property
    def mistake(self):
        return self.__mistake

    @mistake.setter
    def mistake(self, value):
        Validator.validate(value, Mistake)
        self.__mistake = value

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
            "mistake": self.mistake.to_dict(),
            "message": self.message,
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.mistake = Mistake()
        self.mistake.from_dict(data.get("mistake", {}))

        self.message = data.get("message", "")

    def __eq__(self, other):
        return super().__eq__(other) and self.mistake == other.mistake and self.message == other.message

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.mistake} - {self.message}"
