from fastapi import Body
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


@router.post(
    "/api/reemployment/analyze",
    response_model=ReemploymentResponse,
    summary="재취업 가능성 분석",
    description="GPT 기반 분석을 통해, 연령/업종/성별에 따른 재취업 가능성을 분석",
    response_description="재취업 가능성 분석 결과",
    responses={
        200: {
            "description": "재취업 분석 예시 응답",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "회원님이 종사하는 광업 분야에는 고령자 근로자 744명(전체 1502명 중)이 근무 중이며, 남성은 약 45.8%인 688명이 종사 중입니다. 해당 업종은 자원 채취 및 생산 기반으로 인해 전문성이 요구되나, 자원 고갈 및 작업 환경의 변화로 인해 재취업 기회는 다소 제한적일 수 있습니다. 지속 가능한 기술 적용과 안전 관리가 중요할 것으로 보입니다."
                    }
                }
            },
        }
    },
)
async def reemployment_analysis_endpoint(
    request: ReemploymentRequest = Body(
        example={"question": "50대, 광업, 남성 재취업 가능성이 궁금해"}
    ),
):
    question = request.question
    result = get_final_reemployment_analysis(question)

    # answer가 dict 일 경우 input을 추출
    answer = result["answer"]
    if isinstance(answer, dict) and "input" in answer:
        answer = answer["input"]

    return ReemploymentResponse(answer=answer)


@router.post(
    "/api/education/search",
    response_model=EducationSearchResponse,
    summary="맞춤형 교육 정보 제공",
    description="선택한 카테고리에 맞는 중장년층 교육 프로그램 정보를 제공",
    response_description="추천된 교육 프로그램 목록",
    responses={
        200: {
            "description": "교육 검색 예시 응답",
            "content": {
                "application/json": {
                    "example": {
                        "results": [
                            {
                                "title": "교육명1",
                                "reg_start_date": "2025.06.16",
                                "reg_end_date": "2025.07.14",
                                "course_start_date": "2025.07.15",
                                "course_end_date": "2025.09.05",
                                "hour": "39:00",
                                "status": "수강신청예정",
                                "url": "url",
                            },
                            {
                                "title": "교육명2",
                                "reg_start_date": "2025.05.26",
                                "reg_end_date": "2025.06.03",
                                "course_start_date": "2025.07.04",
                                "course_end_date": "2025.07.25",
                                "hour": "49:30",
                                "status": "수강신청예정",
                                "url": "url",
                            },
                        ]
                    }
                }
            },
        }
    },
)
def education_search(
    request: EducationSearchRequest = Body(
        example={
            "category": "디지털기초역량/사무행정실무/전문기술자격증/서비스 직무교육 중 버튼 선택 1"
        }
    ),
):
    xml_data = fetch_education_data()
    filtered_results = parse_education_xml(xml_data, request.category)
    return {"results": filtered_results}


@router.post(
    "/api/policy/recommend",
    response_model=PolicyRecommendResponse,
    summary="고용 정책/복지 안내",
    description="선택한 복지 카테고리에 맞는 고용 정책 정보를 GPT 기반 RAG 시스템으로 추천.",
    response_description="추천된 고용 정책 목록",
    responses={
        200: {
            "description": "정책 추천 예시 응답",
            "content": {
                "application/json": {
                    "example": {
                        "message": "[카테고리]의 복지 정보는 다음과 같습니다.",
                        "results": [
                            {
                                "title": "복지1",
                                "description": "설명1",
                                "url": "url",
                            },
                            {
                                "title": "복지2",
                                "description": "설명2",
                                "url": "url",
                            },
                        ],
                    }
                }
            },
        }
    },
)
async def policy_recommend(
    req: PolicyRecommendRequest = Body(
        example={
            "category": "디지털기초역량/사무행정실무/전문기술자격증/서비스 직무교육 중 버튼 선택 1"
        }
    ),
):
    policies = recommend_policy_by_category(req.category)

    return PolicyRecommendResponse(
        message=f"[{req.category}]의 복지 정보는 다음과 같습니다.", results=policies
    )


@router.post(
    "/api/education/bookmark",
    summary="교육 정보 북마크",
    description="사용자가 선택한 교육 정보를 데이터베이스에 북마크로 저장합니다.",
    response_description="북마크 저장 결과 메시지",
    responses={
        200: {
            "description": "북마크 성공 예시",
            "content": {
                "application/json": {"example": {"message": "교육 정보 북마크 성공."}}
            },
        }
    },
)
def bookmark_education(
    data: EducationBookmarkRequest = Body(
        example={
            "user_id": 1,
            "bookmarks": [
                {
                    "title": "교육1",
                    "url": "https://example.com/edu1",
                },
                {
                    "title": "교육2",
                    "url": "https://example.com/edu2",
                },
            ],
        }
    ),
    db: Session = Depends(get_db),
):
    return save_bookmarked_education(data, db)


@router.post(
    "/api/policy/bookmark",
    summary="복지 정보 북마크",
    description="사용자가 선택한 복지 정보를 데이터베이스에 북마크로 저장합니다.",
    response_description="북마크 저장 결과 메시지",
    responses={
        200: {
            "description": "북마크 성공 예시",
            "content": {
                "application/json": {"example": {"message": "복지 정보 북마크 성공."}}
            },
        }
    },
)
def bookmark_policy(
    data: PolicySaveRequest = Body(
        example={
            "user_id": 1,
            "policies": [
                {
                    "title": "정책1",
                    "category": "직업 훈련 지원",
                    "description": "설명1",
                    "url": "https://example.com/policy1",
                },
                {
                    "title": "정책2",
                    "category": "직업 훈련 지원",
                    "description": "설명2",
                    "url": "https://example.com/policy2",
                },
            ],
        }
    ),
    db: Session = Depends(get_db),
):
    return save_policy_bookmarks(data, db)
