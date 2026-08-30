"""Public personality-type payload. Matches seeded educational copy."""

from pydantic import BaseModel, ConfigDict, Field


class PersonalityTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    tagline: str
    description: str
    characteristics: list[str]
    strengths: list[str]
    development_areas: list[str]
    communication_style: str
    work_style: str
    career_environments: str
    development_suggestions: str
    disclaimer: str = Field(
        description="Shown so results are not mistaken for a clinical diagnosis."
    )
