from enum import Enum


class EventType(Enum):
    """Типы событий"""

    LOG_INFO = 1
    LOG_ERROR = 2
    LOG_DEBUG = 3
