"""User payloads returned to the client. Never includes password_hash."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.email import EmailAddress

from app.models.enums import AgeGroup, Gender


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
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    gender: Gender | None = None
    age_group: AgeGroup | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
