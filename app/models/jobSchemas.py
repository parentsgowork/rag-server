from pydantic import BaseModel
from typing import List
from app.models.common import TimestampMixin


class JobSummary(BaseModel):
    title: str
    description: str


class JobSummaryResponse(BaseModel):
    count: int
    results: List[JobSummary]
