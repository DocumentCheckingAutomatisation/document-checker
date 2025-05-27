from enum import Enum


class RuleType(Enum):
    """Типы ошибок"""

    COMMON = 1
    STRUCTURE = 2
    INTRO_KEYWORDS = 3
    CHAPTER = 4
    SECTION = 5
    PICTURE = 6
    TABLE = 7
    LIST = 8
    FORMULA = 9
    BIBLIOGRAPHY = 10
    APPLICATION = 11
    QUOTES = 12



