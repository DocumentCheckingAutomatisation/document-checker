from enum import Enum


class RuleType(Enum):
    """Типы правил"""

    COMMON = 1
    STRUCTURE = 2
    CHAPTER_HEADING = 3
    SECTION_HEADING = 4
    SUBSECTION_HEADING = 5
    PICTURE = 6
    TABLE = 7
    LIST = 8
    FORMULA = 9



