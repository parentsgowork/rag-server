from pydantic import BaseModel
from typing import List
from app.models.common import TimestampMixin


class PolicyRecommendRequest(BaseModel):
    category: str


class PolicyInfo(BaseModel):
    title: str
    description: str
    url: str


class PolicyRecommendResponse(BaseModel):
    message: str
    results: List[PolicyInfo]


class PolicyItem(BaseModel):
    title: str
    category: str
    description: str
    url: str


class PolicySaveRequest(TimestampMixin):
    user_id: int
    policies: List[PolicyItem]
