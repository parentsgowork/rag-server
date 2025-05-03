from pydantic import BaseModel
from typing import List


class EducationSearchRequest(BaseModel):
    category: str  # ex: 디지털기초역량


class EducationInfo(BaseModel):
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
