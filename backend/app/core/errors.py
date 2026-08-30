"""Application errors that become the standard JSON envelope."""


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        errors: list | dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors
