# Pydantic Request/Response 모델
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.models.common import TimestampMixin


class ReemploymentRequest(BaseModel):
    question: str


class ReemploymentResponse(BaseModel):
    answer: str
    reemployment_score: int  # 0 ~ 100
    market_fit: str  # "높음", "보통", "낮음"
    summary: str
