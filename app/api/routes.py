# fast api 엔드포인트 모음
from fastapi import APIRouter
from app.models.schemas import ReemploymentRequest, ReemploymentResponse
from app.services.rag_service import analyze_reemployment_possibility

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.post("/reemployment-analysis", response_model=ReemploymentResponse)
async def reemployment_analysis(request: ReemploymentRequest):
    result = analyze_reemployment_possibility(request.question)
    return ReemploymentResponse(
        answer=result["answer"],
        sources=result["sources"]
    )