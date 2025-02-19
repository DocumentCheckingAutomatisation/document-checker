from src.models.mistake import Mistake
from src.core.abstract_model import AbstractModel

class Recomendation(AbstractModel):
    def __init__(self, name=None, id=None, mistake=None, message=None):
        super().__init__(name, id)
        self.mistake: Mistake = mistake or Mistake()
        self.message: str = message or ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "mistake": self.mistake.to_dict(),
            "message": self.message,
        }

    def from_json(self, data: dict):
        super().from_json(data)

        self.mistake = Mistake().from_json(data.get("mistake", {}))
        self.message = data.get("message", "")

    def __eq__(self, other):
        return super().__eq__(other) and self.mistake == other.mistake and self.message == other.message

    def __str__(self):
        return f"{self.name} ({self.id}) - {self.mistake} - {self.message}"