from pydantic import BaseModel
from typing import List
from app.models.common import TimestampMixin


class EducationSearchRequest(BaseModel):
    category: str


class EducationInfo(BaseModel):  # Pydantic용
    title: str
    reg_start_date: str
    reg_end_date: str
    course_start_date: str
    course_end_date: str
    hour: str
    status: str
    url: str


class EducationSearchResponse(BaseModel):
    results: List[EducationInfo]


class EducationItem(BaseModel):
    title: str
    url: str


class EducationBookmarkRequest(BaseModel):
    bookmarks: List[EducationItem]
