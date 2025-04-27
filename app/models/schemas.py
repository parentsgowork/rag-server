# Pydantic Request/Response 모델
from pydantic import BaseModel
from typing import List, Dict, Optional

class ReemploymentRequest(BaseModel):
    question: str

class ReemploymentResponse(BaseModel):
    answer: str
    sources: List[Dict]
    age_group: Optional[str]
    field: Optional[str]