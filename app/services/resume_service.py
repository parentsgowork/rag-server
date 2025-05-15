import uuid
import json
from sqlalchemy.orm import Session
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.db_models.resume import Resume
from app.models.resumeSchemas import ResumeSaveRequest
from app.models.resumeSchemas import ResumeResult

llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# 카테고리 순서 및 질문 텍스트 정의
CATEGORY_ORDER = ["성장과정", "지원동기", "입사포부", "강점약점", "프로젝트경험"]
QUESTION_MAP = {
    "성장과정": "성장과정에 대해 말씀해주세요.",
    "지원동기": "해당 기업에 지원하게 된 동기는 무엇인가요?",
    "입사포부": "입사 후 이루고 싶은 목표는 무엇인가요?",
    "강점약점": "자신의 강점과 약점을 솔직히 말해주세요.",
    "프로젝트경험": "인상 깊은 프로젝트 경험을 말해주세요.",
}

# 항목별 LangChain 프롬프트 템플릿
PROMPT_TEMPLATES = {
    "성장과정": PromptTemplate.from_template(
        """
[회사명]: {company}
[직무]: {position}
[사용자 답변]: {user_input}

위 내용을 바탕으로 성장과정을 진솔하고 정중한 자기소개서 문장으로 작성해주세요.
"""
    ),
    "지원동기": PromptTemplate.from_template(
        """
[회사명]: {company}
[직무]: {position}
[사용자 답변]: {user_input}

사용자의 답변을 참고하여 해당 기업에 지원한 동기를 설득력 있게 자기소개서 형식으로 작성해주세요.
"""
    ),
    "입사포부": PromptTemplate.from_template(
        """
[회사명]: {company}
[직무]: {position}
[사용자 답변]: {user_input}

입사 후 이루고 싶은 포부를 자신감 있게 자기소개서 문장으로 작성해주세요.
"""
    ),
    "강점약점": PromptTemplate.from_template(
        """
[회사명]: {company}
[직무]: {position}
[사용자 답변]: {user_input}

강점과 약점을 조화롭게 표현하고, 약점은 개선 의지를 포함하여 작성해주세요.
"""
    ),
    "프로젝트경험": PromptTemplate.from_template(
        """
[회사명]: {company}
[직무]: {position}
[사용자 답변]: {user_input}

해당 프로젝트 경험을 자기소개서 항목처럼 구체적으로 작성해주세요.
"""
    ),
}

# 메모리 기반 세션 저장소
SESSIONS = {}


def init_session(company: str, position: str):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "company": company,
        "position": position,
        "answers": {},
        "current_index": 0,
    }
    first_category = CATEGORY_ORDER[0]
    return session_id, first_category, QUESTION_MAP[first_category]


def generate_ai_answer(category: str, user_input: str, company: str, position: str):
    prompt = PROMPT_TEMPLATES[category].format(
        company=company, position=position, user_input=user_input
    )
    return llm.invoke(prompt).content


def process_user_answer(session_id: str, user_input: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise ValueError("존재하지 않는 세션입니다.")

    idx = session["current_index"]
    if idx >= len(CATEGORY_ORDER):
        raise ValueError("모든 질문이 완료되었습니다.")

    category = CATEGORY_ORDER[idx]

    # AI 응답 생성
    ai_response = generate_ai_answer(
        category, user_input, session["company"], session["position"]
    )
    session["answers"][category] = ai_response
    session["current_index"] += 1

    # 다음 질문 준비
    if session["current_index"] < len(CATEGORY_ORDER):
        next_category = CATEGORY_ORDER[session["current_index"]]
        next_question = QUESTION_MAP[next_category]
        return {
            "current_category": category,
            "ai_response": ai_response,
            "next_category": next_category,
            "next_question": next_question,
            "is_last": False,
        }
    else:
        return {
            "current_category": category,
            "ai_response": ai_response,
            "is_last": True,
        }


def get_resume(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise ValueError("세션을 찾을 수 없습니다.")

    return {
        "title": f"{session['company']} {session['position']} 지원 자기소개서",
        "sections": session["answers"],
    }


def save_resume_to_db(user_id: int, db: Session, data: ResumeSaveRequest):
    content_json_str = json.dumps(data.sections, ensure_ascii=False)
    resume = Resume(
        user_id=user_id,
        title=data.title,
        content=content_json_str,
        resume_category=data.resume_category,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def get_resumes_by_user_id(db: Session, user_id: int) -> list[ResumeResult]:
    resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
    result = []
    for r in resumes:
        try:
            content_dict = json.loads(r.content)
        except json.JSONDecodeError:
            content_dict = {}

        result.append(
            ResumeResult(
                title=r.title,
                sections=content_dict,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return result
