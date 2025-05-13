from fastapi import APIRouter, Depends, Body, Query
from app.utils.jwt import verify_jwt
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.models.resumeSchemas import (
    ResumeInitRequest,
    ResumeAnswerRequest,
    ResumeSaveRequest,
    ResumeResult,
)

from app.services.resume_service import (
    init_session,
    process_user_answer,
    get_resume,
    save_resume_to_db,
    get_resumes_by_user_id,
)

from app.models.reempSchemas import ReemploymentRequest, ReemploymentResponse
from app.services.reemp_service import get_final_reemployment_analysis

from app.models.eduSchemas import (
    EducationSearchRequest,
    EducationSearchResponse,
    EducationBookmarkRequest,
)
from app.services.education_service import (
    fetch_education_data,
    parse_education_xml,
    save_bookmarked_education,
)

from app.models.policySchemas import (
    PolicyRecommendRequest,
    PolicyRecommendResponse,
    PolicySaveRequest,
)
from app.services.policy_service import (
    recommend_policy_by_category,
    save_policy_bookmarks,
)

from app.services.job_service import recommend_jobs
from app.models.jobSchemas import JobRecommendation

router = APIRouter()


@router.get(
    "/api/job/recommend",
    tags=["사용자 맞춤 구직 추천"],
    response_model=list[JobRecommendation],
    summary="사용자 맞춤 구직 추천",
    description="user_id에 기반하여 서울시 구인공고 중 사용자 조건에 맞는 구직 정보를 추천하고, 각 항목에 대해 GPT 기반 설명을 포함하여 반환합니다.",
    response_description="추천된 구직 리스트",
    responses={
        200: {
            "description": "구직 추천 응답 예시",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "jo_reqst_no": "H954202505090864",
                            "jo_regist_no": "K120122505090018",
                            "company_name": "늘섬김 재가복지센터",
                            "job_title": "제기동 90세 4등급 10:30-13:30 주5일 할머니 모실 요양보호사 모십니다.",
                            "description": "우대사항: 고령자 이동 지원, 목욕 등 신체 활동 지원, 가사 및 일상 생활 지원, 정서 지원에 능한 요양보호사\n\n직무 특징: 90세의 4등급 할머니를 주 5일, 오전 10시 30분부터 오후 1시 30분까지 돌봐야 합니다. 실내에서는 이동식 보행기를 이용하며, 외출 시에는 휠체어를 이용합니다. 인지력이 좋아 본인 의사를 잘 전달하며, 딸이 주말에 필요한 물품을 챙겨줍니다. 시급은 10,030원이며 기초 수당이 별도로 제공됩니다.",
                            "deadline": "마감일 (2025-07-08)",
                            "location": "서울 동대문구.",
                            "pay": "시급 / 10030원 ",
                            "registration_date": "2025-05-09",
                            "time": "(근무시간) (오전) 10시 30분 ~ (오후) 1시 30분",
                        }
                    ]
                }
            },
        }
    },
)
def recommend_job_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    token_data=Depends(verify_jwt),
):
    return recommend_jobs(user_id, db)


@router.post(
    "/api/reemployment/analyze",
    tags=["재취업 가능성 분석"],
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
                        "answer": "회원님이 종사하는 광업 분야에는 고령자 근로자 744명(전체 1502명 중)이 근무 중이며, 남성은 약 45.8%인 688명이 종사 중입니다. 해당 업종은 자원 채취 및 생산 기반으로 인해 전문성이 요구되나, 자원 고갈 및 작업 환경의 변화로 인해 재취업 기회는 다소 제한적일 수 있습니다. 지속 가능한 기술 적용과 안전 관리가 중요할 것으로 보입니다.",
                        "reemployment_score": 85,
                        "market_fit": "높음",
                        "summary": "귀하의 기술 역량과 경력이 현재 시장 수요와 잘 부합합니다.",
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
    token_data=Depends(verify_jwt),
):
    question = request.question
    result = get_final_reemployment_analysis(question)
    return ReemploymentResponse(**result)


@router.post(
    "/api/education/search",
    tags=["교육 정보"],
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
    token_data=Depends(verify_jwt),
):
    xml_data = fetch_education_data()
    filtered_results = parse_education_xml(xml_data, request.category)
    return {"results": filtered_results}


@router.post(
    "/api/education/bookmark",
    tags=["교육 정보"],
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
    token_data=Depends(verify_jwt),
):
    return save_bookmarked_education(data, db)


@router.post(
    "/api/policy/recommend",
    tags=["고용 정책/복지"],
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
            "category": "취업 지원금/직업 훈련 지원/고용 안정 지원/생활 안정 지원 중 버튼 선택 1"
        }
    ),
    token_data=Depends(verify_jwt),
):
    policies = recommend_policy_by_category(req.category)

    return PolicyRecommendResponse(
        message=f"[{req.category}]의 복지 정보는 다음과 같습니다.", results=policies
    )


@router.post(
    "/api/policy/bookmark",
    tags=["고용 정책/복지"],
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
    token_data=Depends(verify_jwt),
):
    return save_policy_bookmarks(data, db)


# 세션 생성 및 첫 번째 질문 반환
@router.post(
    "/api/resume/init",
    tags=["AI 자기소개서"],
    summary="자기소개서 세션 시작",
    description="입사할 회사명과 직무를 입력받아 자기소개서 작성을 위한 세션을 초기화하고 첫 번째 질문을 반환.",
)
def init(data: ResumeInitRequest, token_data=Depends(verify_jwt)):
    """
    입력:
    - company: 지원 회사명
    - position: 지원 직무명

    출력:
    - session_id: 고유 세션 ID
    - category: 현재 질문 항목 (예: '성장과정')
    - question: 사용자에게 보여줄 질문 텍스트
    """
    session_id, category, question = init_session(data.company, data.position)
    return {"session_id": session_id, "category": category, "question": question}


# 사용자 입력 저장 + 해당 항목의 GPT 응답 생성 -> 다음 질문 반환
@router.post(
    "/api/resume/answer",
    tags=["AI 자기소개서"],
    summary="사용자 입력에 대한 AI 응답 생성",
    description="현재 질문에 대한 사용자의 답변을 받아 AI가 해당 항목의 자기소개서 문장을 생성. 이후 다음 질문 항목도 함께 반환.",
)
def answer(data: ResumeAnswerRequest, token_data=Depends(verify_jwt)):
    """
    입력:
    - session_id: 기존 생성된 세션 ID
    - user_input: 사용자 입력 내용 (해당 항목에 대한 자유 입력)

    출력:
    - current_category: 방금 답변한 항목명
    - ai_response: AI가 생성한 자기소개서 문장
    - next_category: 다음 질문 항목명 (마지막이면 없음)
    - next_question: 다음 질문 텍스트
    - is_last: True면 마지막 항목
    """
    return process_user_answer(data.session_id, data.user_input)


# 완성된 자기소개서 반환
@router.get(
    "/api/resume/result/{session_id}",
    tags=["AI 자기소개서"],
    summary="최종 자기소개서 결과 조회",
    description="해당 세션 ID에 대해 지금까지 작성된 모든 자기소개서 항목과 내용을 반환.",
    response_model=ResumeResult,
)
def result(session_id: str, token_data=Depends(verify_jwt)):
    """
    입력:
    - session_id: 자기소개서 작성 세션 ID

    출력:
    - title: '삼성전자 소프트웨어 개발자 지원 자기소개서' 형태의 제목
    - sections: 카테고리별 작성된 AI 자기소개서 텍스트 (딕셔너리 형태)
    """
    return get_resume(session_id)


@router.post(
    "/api/resume/save",
    tags=["AI 자기소개서"],
    summary="자기소개서 저장",
    description="완성된 자기소개서를 DB에 저장합니다. 저장된 content는 JSON 문자열로 저장되며, resume_category와 제목도 함께 저장됩니다.",
    response_description="저장 결과 메시지 및 생성된 resume_id",
    responses={
        200: {
            "description": "자기소개서 저장 성공 응답",
            "content": {
                "application/json": {
                    "example": {
                        "resume_id": 12,
                        "message": "자기소개서가 저장되었습니다.",
                    }
                }
            },
        },
        400: {
            "description": "입력 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "입력 값이 유효하지 않습니다."}
                }
            },
        },
    },
)
def save_resume(
    data: ResumeSaveRequest = Body(
        example={
            "user_id": 1,
            "title": "삼성전자 백엔드 개발자 지원 자기소개서",
            "sections": {
                "성장과정": "...",
                "지원동기": "...",
                "입사포부": "...",
                "강점약점": "...",
                "프로젝트경험": "...",
            },
            "resume_category": "TECH",
        }
    ),
    db: Session = Depends(get_db),
    token_data=Depends(verify_jwt),
):
    saved = save_resume_to_db(db, data)
    return {"resume_id": saved.id, "message": "자기소개서가 저장되었습니다."}


@router.get(
    "/api/resume/user/{userId}",
    tags=["AI 자기소개서"],
    response_model=list[ResumeResult],
    summary="사용자의 자기소개서 목록 조회",
    description="특정 user_id에 해당하는 사용자가 저장한 자기소개서 리스트를 조회합니다. 각 자기소개서는 title과 sections(JSON 파싱된 dict 형태)로 반환됩니다.",
    response_description="자기소개서 목록",
    responses={
        200: {
            "description": "조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "title": "삼성전자 백엔드 개발자 지원 자기소개서",
                            "sections": {
                                "성장과정": "...",
                                "지원동기": "...",
                                "입사포부": "...",
                                "강점약점": "...",
                                "프로젝트경험": "...",
                            },
                        }
                    ]
                }
            },
        },
        404: {
            "description": "해당 사용자의 자기소개서가 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "자기소개서가 존재하지 않습니다."}
                }
            },
        },
    },
)
def get_user_resumes(
    userId: int, db: Session = Depends(get_db), token_data=Depends(verify_jwt)
):
    return get_resumes_by_user_id(db, userId)


@router.get("/ping")
async def ping():
    return {"message": "pong"}
