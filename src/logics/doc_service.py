from src.core.abstract_logic import AbstractLogic
from src.core.doc_type import DocType
from src.core.event_type import EventType
from src.logics.observe_service import ObserveService


class DocService(AbstractLogic):

    def __init__(self):
        ObserveService.append(self)

    @staticmethod
    def get_doc_types():
        return [{"name": doc.name, "value": doc.value} for doc in DocType]

    def set_exception(self, ex: Exception):
        super().set_exception(ex)

    def handle_event(self, event_type: EventType, params):
        super().handle_event(event_type, params)