from typing import Any


class error(Exception):
    def __init__(self, message: Any = None):
        if message is not None:
            self.message = str(message)
        else:
            self.message = None
        super().__init__(self.message)

    def __str__(self) -> str | None:
        return self.message

    def __eq__(self, value: object, /) -> bool:
        if hasattr(value, "message"):
            return self.message == value.message
        return self.message == value

    def __ne__(self, value: object, /) -> bool:
        if hasattr(value, "message"):
            return self.message != value.message
        return self.message != value


class httpError(error):
    def __init__(self, code: int, message: str = None):
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} {self.code}"

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, httpError):
            return self.code == value.code and self.message == value.message
        if hasattr(value, "message"):
            return self.message == value.message
        return self.message == value

    def __ne__(self, value: object, /) -> bool:
        result = self.__eq__(value)
        return not result if result is not NotImplemented else NotImplemented


type Error = error | httpError | None
InternaleServerError = httpError(500, "Internal server error")
