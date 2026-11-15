"""HTTP security headers applied to every response.

These do not replace HTTPS in production. They stop common browser
misuses of a JSON API: MIME sniffing, framing, and referrer leaks.
"""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response

CallNext = Callable[[Request], Awaitable[Response]]

HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cache-Control": "no-store",
}


async def add_security_headers(request: Request, call_next: CallNext) -> Response:
    response = await call_next(request)
    for name, value in HEADERS.items():
        response.headers.setdefault(name, value)
    return response
