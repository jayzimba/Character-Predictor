"""Shared password rules. bcrypt silently truncates above 72 bytes."""

import re

_PASSWORD_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_DIGIT = re.compile(r"\d")
BCRYPT_MAX_BYTES = 72


def validate_password_complexity(password: str) -> str:
    if len(password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise ValueError("Password must be at most 72 bytes")
    if not _PASSWORD_LETTER.search(password) or not _PASSWORD_DIGIT.search(password):
        raise ValueError("Password must contain at least one letter and one number")
    return password
