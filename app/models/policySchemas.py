from pydantic import BaseModel
from typing import List


class PolicyRecommendRequest(BaseModel):
    category: str


class PolicyInfo(BaseModel):
    title: str
    description: str
    url: str


class PolicyRecommendResponse(BaseModel):
    message: str
    results: List[PolicyInfo]
