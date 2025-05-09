# Pydantic Request/Response 모델
from pydantic import BaseModel
from typing import List, Dict, Optional


class ReemploymentRequest(BaseModel):
    question: str


class ReemploymentResponse(BaseModel):
    answer: str
    reemployment_score: int  # 0 ~ 100
    market_fit: str  # "높음", "보통", "낮음"
    summary: str
