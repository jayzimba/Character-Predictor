"""User payloads returned to the client. Never includes password_hash."""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import AgeGroup, Gender
from app.schemas.email import EmailAddress
from app.schemas.passwords import validate_password_complexity


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailAddress
    gender: str | None = None
    age_group: str | None = None
    is_active: bool
    role: RoleOut


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    gender: Gender | None = None
    age_group: AgeGroup | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)
    confirm_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        return validate_password_complexity(value)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
