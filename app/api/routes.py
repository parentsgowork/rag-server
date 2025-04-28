# fast api 엔드포인트 모음
from fastapi import APIRouter
from app.models.schemas import ReemploymentRequest, ReemploymentResponse
from app.services.rag_service import get_final_reemployment_analysis

router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.post("/reemployment-analysis", response_model=ReemploymentResponse)
async def reemployment_analysis_endpoint(request: ReemploymentRequest):
    question = request.question
    result = get_final_reemployment_analysis(question)

    return ReemploymentResponse(
        answer=result["answer"],
        sources=result["sources"],
        age_group=result.get("age_group"),
        field=result.get("field")
    )