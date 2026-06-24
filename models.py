"""Pydantic models for request/response validation."""

from pydantic import BaseModel, field_validator
from typing import Optional


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class AskResponse(BaseModel):
    answer: str
    incident_id: Optional[str] = None
    severity: Optional[str] = None


class Incident(BaseModel):
    id: str
    service: str
    severity: str
    status: str = "Open"
