class ArgumentException(Exception):
    """Исключение при проверке аргумента"""
    pass


class OperationException(Exception):
    """Исключение при выполнении бизнес операции"""
    pass


class Validator:
    """Набор проверок данных"""

    @staticmethod
    def validate(value, type_, len_=None):
        """
            Валидация аргумента по типу и длине
        Args:
            value (any): Аргумент
            type_ (object): Ожидаемый тип
            len_ (int): Максимальная длина
        Raises:
            arguent_exception: Некорректный тип
            arguent_exception: Неулевая длина
            arguent_exception: Некорректная длина аргумента
        Returns:
            True или Exception
        """

        if value is None:
            raise ArgumentException(f"Пустой аргумент {type(value)}")

        # Проверка типа
        # if not isinstance(value, type_):
        #     raise argument_exception("Некорректный тип")
        if isinstance(type_, type):
            if not isinstance(value, type_):
                raise ArgumentException(f"Некорректный тип. Ожидался {type_}, получен {type(value)}.")
        else:
            raise ArgumentException("Передан некорректный тип для проверки.")

        # Проверка аргумента
        if len(str(value).strip()) == 0:
            raise ArgumentException(f"Пустой аргумент {type(value)}")

        if len_ is not None and len(str(value).strip()) >= len_:
            raise ArgumentException("Некорректная длина аргумента")

        return True
