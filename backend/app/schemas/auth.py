"""Authentication request and token response schemas."""

import re

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import AgeGroup, Gender
from app.schemas.email import EmailAddress
from app.schemas.user import UserOut

_PASSWORD_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_DIGIT = re.compile(r"\d")


def validate_password_complexity(password: str) -> str:
    if not _PASSWORD_LETTER.search(password) or not _PASSWORD_DIGIT.search(password):
        raise ValueError("Password must contain at least one letter and one number")
    return password


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailAddress
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
    gender: Gender | None = None
    age_group: AgeGroup | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailAddress) -> str:
        return str(value).strip().lower()

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        return validate_password_complexity(value)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailAddress) -> str:
        return str(value).strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class PasswordResetRequest(BaseModel):
    email: EmailAddress

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailAddress) -> str:
        return str(value).strip().lower()


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=16)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        return validate_password_complexity(value)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
