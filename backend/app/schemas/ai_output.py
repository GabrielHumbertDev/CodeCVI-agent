"""
Pydantic schemas for validating AI-generated output.
These are used internally by services — not exposed as API response models.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class ExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    dates: str = ""
    description: str = ""

    @field_validator("title", "company", mode="before")
    @classmethod
    def coerce_str(cls, v: object) -> str:
        return str(v) if v is not None else ""


class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    dates: str = ""

    @field_validator("degree", "institution", mode="before")
    @classmethod
    def coerce_str(cls, v: object) -> str:
        return str(v) if v is not None else ""


class TailoredCVOutput(BaseModel):
    """Schema for the JSON object returned by the CV tailoring AI."""

    name: str
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: list[str] = []
    experience: list[ExperienceItem] = []
    education: list[EducationItem] = []

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("skills", mode="before")
    @classmethod
    def skills_must_be_list(cls, v: object) -> list:
        if isinstance(v, str):
            # AI sometimes returns comma-separated string
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [str(s) for s in v]
        return []

    @field_validator("experience", mode="before")
    @classmethod
    def experience_must_be_list(cls, v: object) -> list:
        if not isinstance(v, list):
            return []
        return v

    @field_validator("education", mode="before")
    @classmethod
    def education_must_be_list(cls, v: object) -> list:
        if not isinstance(v, list):
            return []
        return v

    @model_validator(mode="after")
    def has_meaningful_content(self) -> "TailoredCVOutput":
        if not self.summary and not self.skills and not self.experience:
            raise ValueError(
                "Tailored CV has no summary, skills, or experience — output appears empty"
            )
        return self


class CoverLetterOutput(BaseModel):
    """Schema for plain-text cover letter output."""

    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Cover letter text is empty")
        if len(stripped) < 100:
            raise ValueError(
                f"Cover letter is too short ({len(stripped)} chars) — likely a failed generation"
            )
        return stripped
