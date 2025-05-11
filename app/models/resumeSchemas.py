from pydantic import BaseModel
from typing import Dict
from enum import Enum


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


class ResumeResult(BaseModel):
    title: str
    sections: Dict[str, str]


class ResumeSaveRequest(BaseModel):
    user_id: int
    title: str
    sections: Dict[str, str]
    resume_category: ResumeCategory
