"""Email normalisation without rejecting reserved test domains such as .local."""

from typing import Annotated

from pydantic import AfterValidator


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("Enter a valid email address")
    local, _, domain = email.partition("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError("Enter a valid email address")
    return email


EmailAddress = Annotated[str, AfterValidator(normalize_email)]
