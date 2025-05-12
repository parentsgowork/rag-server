from pydantic import BaseModel
from typing import Dict
from enum import Enum
from app.models.common import TimestampMixin


class ResumeInitRequest(BaseModel):
    company: str
    position: str


class ResumeAnswerRequest(BaseModel):
    session_id: str
    user_input: str


class ResumeAnswerResponse(BaseModel):
    ai_response: str


class ResumeCategory(str, Enum):
    GENERAL = "GENERAL"
    TECH = "TECH"
    CAREER = "CAREER"
    ACADEMIC = "ACADEMIC"


class ResumeResult(TimestampMixin):
    title: str
    sections: Dict[str, str]


class ResumeSaveRequest(TimestampMixin):
    user_id: int
    title: str
    sections: Dict[str, str]
    resume_category: ResumeCategory
