from pydantic import BaseModel
from typing import Dict
from enum import Enum
from datetime import datetime
from typing import Optional


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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ResumeSaveRequest(BaseModel):
    title: str
    sections: Dict[str, str]
    resume_category: ResumeCategory
