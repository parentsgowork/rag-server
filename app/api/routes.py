from fastapi import APIRouter
from app.models.schemas import ReemploymentRequest, ReemploymentResponse
from app.services.rag_service import get_final_reemployment_analysis
from app.db_models.education import EducationInfo
from app.models.eduSchemas import EducationSearchRequest, EducationSearchResponse
from app.services.education_service import fetch_education_data, parse_education_xml
from app.models.policySchemas import PolicyRecommendRequest, PolicyRecommendResponse
from app.services.policy_service import recommend_policy_by_category
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.eduSchemas import EducationBookmarkRequest
from app.services.education_service import save_bookmarked_education
from app.models.policySchemas import PolicySaveRequest
from app.services.policy_service import save_policy_bookmarks

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"message": "pong"}


@router.post("/reemployment-analysis", response_model=ReemploymentResponse)
async def reemployment_analysis_endpoint(request: ReemploymentRequest):
    question = request.question
    result = get_final_reemployment_analysis(question)

    # answer가 dict 일 경우 input을 추출
    answer = result["answer"]
    if isinstance(answer, dict) and "input" in answer:
        answer = answer["input"]

    return ReemploymentResponse(answer=answer)


@router.post("/api/education-search", response_model=EducationSearchResponse)
def education_search(request: EducationSearchRequest):
    xml_data = fetch_education_data()
    filtered_results = parse_education_xml(xml_data, request.category)
    return {"results": filtered_results}


@router.post("/api/policy-recommend", response_model=PolicyRecommendResponse)
async def policy_recommend(req: PolicyRecommendRequest):
    policies = recommend_policy_by_category(req.category)

    return PolicyRecommendResponse(
        message=f"[{req.category}]의 복지 정보는 다음과 같습니다.", results=policies
    )


@router.post("/education/bookmark")
def bookmark_education(data: EducationBookmarkRequest, db: Session = Depends(get_db)):
    return save_bookmarked_education(data, db)


@router.post("/api/policy")
def bookmark_policy(data: PolicySaveRequest, db: Session = Depends(get_db)):
    return save_policy_bookmarks(data, db)
