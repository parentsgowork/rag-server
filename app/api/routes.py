# fast api 엔드포인트 모음
from fastapi import APIRouter
from app.models.schemas import ReemploymentRequest, ReemploymentResponse
from app.services.rag_service import analyze_and_extract_profile

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.post("/reemployment-analysis", response_model=ReemploymentResponse)
async def reemployment_analysis(request: ReemploymentRequest):
    result = analyze_and_extract_profile(request.question)
    return ReemploymentResponse(
        answer=result["answer"],
        sources=result["sources"],
        age_group=result["age_group"],
        field=result["field"]
    )