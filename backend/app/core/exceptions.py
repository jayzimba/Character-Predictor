"""Map infrastructure failures to the standard API envelope.

Defence note: clients never see raw SQLAlchemy traces. Operators still
get the real exception in the server log.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.errors import AppError
from app.core.responses import error_response

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return error_response(
            message=exc.message,
            errors=exc.errors,
            status_code=exc.status_code,
        )

    @app.exception_handler(OperationalError)
    async def database_unavailable_handler(
        request: Request,
        exc: OperationalError,
    ):
        logger.error("Database unavailable on %s %s", request.method, request.url.path)
        return error_response(
            message="Database is unavailable. Please try again later.",
            status_code=503,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error on %s %s", request.method, request.url.path)
        return error_response(
            message="A database error occurred.",
            status_code=500,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        # Field path and message only — never echo submitted values (passwords).
        details = [
            {
                "field": ".".join(str(part) for part in err.get("loc", [])),
                "message": err.get("msg"),
            }
            for err in exc.errors()
        ]
        return error_response(
            message="Validation failed",
            errors=details,
            status_code=422,
        )
