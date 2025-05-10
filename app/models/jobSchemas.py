from pydantic import BaseModel
from typing import List


class UserPreference(BaseModel):
    region: str
    career: str
    education: str
    work_type: List[str]


class JobPosting(BaseModel):
    title: str
    region: str
    career: str
    education: str
    work_type: str


class JobRecommendationResponse(BaseModel):
    recommendations: List[JobPosting]
