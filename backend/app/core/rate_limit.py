"""In-memory sliding-window limiter for auth endpoints.

This is enough for a local demonstration. A deployed system would use
Redis or an API gateway. Failed checks return 429 through AppError.
"""

from collections import defaultdict, deque
from threading import Lock
from time import time

from fastapi import Request

from app.core.errors import AppError


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self.window_seconds
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_calls:
                return False
            bucket.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_auth_limiter = SlidingWindowLimiter(max_calls=20, window_seconds=60)


def reset_auth_limiter() -> None:
    _auth_limiter.reset()


def limit_auth_attempts(request: Request) -> None:
    host = request.client.host if request.client else "unknown"
    if not _auth_limiter.allow(f"auth:{host}"):
        raise AppError(
            "Too many authentication attempts. Please wait a minute.",
            status_code=429,
        )
