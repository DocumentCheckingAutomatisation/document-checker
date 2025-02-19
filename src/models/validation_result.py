from src.core.abstract_model import AbstractModel
from src.models.mistake import Mistake
from src.models.recomendation import Recomendation

class ValidationResult(AbstractModel):
    def __init__(self, name=None, id=None, mistakes=None, recomendations=None):
        super().__init__(name, id)
        self.mistakes = mistakes or []
        self.recomendations = recomendations or []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mistakes": [mistake.to_dict() for mistake in self.mistakes],
            "recomendations": [recomendation.to_dict() for recomendation in self.recomendations],
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.mistakes = [Mistake().from_json(mistake) for mistake in data.get("mistakes", [])]
        self.recomendations = [Recomendation().from_json(recomendation) for recomendation in data.get("recomendations", [])]

    def __eq__(self, other):
        return super().__eq__(
            other) and self.mistakes == other.mistakes and self.recomendations == other.recomendations

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.mistakes} - {self.recomendations}"
