"""Standard JSON envelope used by every API response.

Defence note: a single shape makes the frontend and the project report simpler.
"""

from typing import Any

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "OK",
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
        },
    )


def error_response(
    message: str,
    errors: Any = None,
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
        },
    )
