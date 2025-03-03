from src.core.abstract_model import AbstractModel
from src.core.validator import Validator
from src.models.mistake import Mistake
from src.models.recommendation import Recommendation


class ValidationResult(AbstractModel):
    __mistakes: list = []
    __recommendations: list = []

    def __init__(self):
        super().__init__()

    @property
    def mistakes(self):
        return self.__mistakes

    @mistakes.setter
    def mistakes(self, value):
        Validator.validate(value, list)
        self.__mistakes = value

    @property
    def recommendations(self):
        return self.__recommendations

    @recommendations.setter
    def recommendations(self, value):
        Validator.validate(value, list)
        self.__recommendations = value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mistakes": [mistake.to_dict() for mistake in self.mistakes],
            "recommendations": [recommendation.to_dict() for recommendation in self.recommendations],
        }

    def from_dict(self, data: dict):
        super().from_dict(data)

        self.mistakes = [Mistake().from_dict(mistake) for mistake in data.get("mistakes", [])]
        self.recommendations = [Recommendation().from_dict(recommendation) for recommendation in
                                data.get("recommendations", [])]

    def __eq__(self, other):
        return super().__eq__(
            other) and self.mistakes == other.mistakes and self.recommendations == other.recommendations

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.mistakes} - {self.recommendations}"
