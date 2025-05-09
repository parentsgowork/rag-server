import json
import difflib
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.core.config import settings

# 실제 업종 데이터 기준 리스트
FIELDS_IN_DATA = [
    "농업 임업 및 어업",
    "광업",
    "제조업",
    "전기 가스 증기 및 공기조절 공급업",
    "수도 하수 및 폐기물 처리 원료 재생업",
    "건설업",
    "도매 및 소매업",
    "운수 및 창고업",
    "숙박 및 음식점업",
    "정보통신업",
    "금융 및 보험업",
    "부동산업",
    "전문 과학 및 기술 서비스업",
    "사업시설 관리 사업 지원 및 임대 서비스업",
    "공공행정 국방 및 사회보장 행정",
    "교육 서비스업",
    "보건업 및 사회복지 서비스업",
    "예술 스포츠 및 여가관련 서비스업",
    "협회 및 단체 수리 및 기타 개인 서비스업",
    "국제 및 외국기관",
]

# 비공식 업종 표현 → 공식 업종명 매핑
FIELD_ALIAS_MAP = {
    # 정보통신
    "it": "정보통신업",
    "it업종": "정보통신업",
    "정보통신": "정보통신업",
    "개발": "정보통신업",
    "프로그래밍": "정보통신업",
    "소프트웨어": "정보통신업",
    "데이터": "정보통신업",
    "코딩": "정보통신업",
    # 제조
    "제조": "제조업",
    "공장": "제조업",
    "생산직": "제조업",
    "라인": "제조업",
    # 건설
    "건설": "건설업",
    "현장": "건설업",
    "시공": "건설업",
    "토목": "건설업",
    "건축": "건설업",
    # 운수 및 창고
    "운송": "운수 및 창고업",
    "운수": "운수 및 창고업",
    "택배": "운수 및 창고업",
    "물류": "운수 및 창고업",
    "배송": "운수 및 창고업",
    "화물": "운수 및 창고업",
    # 교육
    "교육": "교육 서비스업",
    "학교": "교육 서비스업",
    "강사": "교육 서비스업",
    "교사": "교육 서비스업",
    "학원": "교육 서비스업",
    # 복지·보건
    "복지": "보건업 및 사회복지 서비스업",
    "간호": "보건업 및 사회복지 서비스업",
    "병원": "보건업 및 사회복지 서비스업",
    "요양": "보건업 및 사회복지 서비스업",
    "돌봄": "보건업 및 사회복지 서비스업",
    "요양보호사": "보건업 및 사회복지 서비스업",
    # 서비스
    "서비스": "사업시설 관리 사업 지원 및 임대 서비스업",
    "청소": "사업시설 관리 사업 지원 및 임대 서비스업",
    "경비": "사업시설 관리 사업 지원 및 임대 서비스업",
    "미화": "사업시설 관리 사업 지원 및 임대 서비스업",
    "보안": "사업시설 관리 사업 지원 및 임대 서비스업",
    # 금융
    "금융": "금융 및 보험업",
    "은행": "금융 및 보험업",
    "보험": "금융 및 보험업",
    "증권": "금융 및 보험업",
    # 공공행정
    "공무원": "공공행정 국방 및 사회보장 행정",
    "행정": "공공행정 국방 및 사회보장 행정",
    "관공서": "공공행정 국방 및 사회보장 행정",
    # 국제기구
    "외국기관": "국제 및 외국기관",
    "국제": "국제 및 외국기관",
    "외교": "국제 및 외국기관",
}


_llm_cache = None  # LLM 캐싱


def get_llm(model="gpt-3.5-turbo"):
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model=model,
            temperature=0,
            max_tokens=600,
        )
    return _llm_cache


def get_vectorstore():
    pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
    index = pc.Index(settings.PINECONE_INDEX_NAME_REEMPLOYMENT)
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-ada-002"
    )
    return PineconeVectorStore(index=index, embedding=embeddings, namespace="default")


def apply_field_alias_fuzzy(raw_field: str):
    field = raw_field.lower()
    if field in FIELD_ALIAS_MAP:
        return FIELD_ALIAS_MAP[field]
    for alias, mapped in FIELD_ALIAS_MAP.items():
        if alias in field:
            return mapped
    matches = difflib.get_close_matches(field, FIELDS_IN_DATA, n=1, cutoff=0.6)
    return matches[0] if matches else raw_field


def extract_field_and_gender(question: str):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                '사용자의 질문에서 재취업 관련 업종(예: 제조업, 광업)과 성별(남성 또는 여성)을 JSON으로 추출하세요. 예시: {{"field": "광업", "gender": "남성"}} 명확하지 않으면 각각 \'일반\', \'모름\'으로 표시하세요.',
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"input": question})
    print("[업종/성별 추출 결과]", result)

    try:
        parsed = json.loads(result)
        field = apply_field_alias_fuzzy(parsed.get("field", "일반").strip())
        gender = parsed.get("gender", "모름").strip()
        if gender not in ["남성", "여성"]:
            gender = "모름"
    except Exception:
        field, gender = "일반", "모름"

    return field, gender


def get_field_stats(field: str, gender: str):
    retriever = get_vectorstore().as_retriever(
        search_kwargs={"k": 1, "filter": {"field": field, "age_group": "55세 이상"}}
    )
    docs = retriever.invoke(f"{field} 업종의 55세 이상 {gender} 근로자 수는?")
    if not docs:
        return None

    content = docs[0].page_content
    print("[검색된 문서]", content)

    try:
        total = int(
            content.split("전체 근로자 수는")[1].split("명")[0].strip().replace(",", "")
        )
        male = int(content.split("남성은")[1].split("명")[0].strip().replace(",", ""))
        female = int(content.split("여성은")[1].split("명")[0].strip().replace(",", ""))
        target = male if gender == "남성" else female
        return {"total": total, "target": target, "raw": content}
    except Exception as e:
        print("파싱 오류:", e)
        return None


def analyze_reemployment(field: str, stats: dict, gender: str):
    total = stats["total"]
    target = stats["target"]
    ratio = round((target / total) * 100) if total > 0 else 0
    score = max(min(ratio + 10, 100), 20)

    if score >= 70:
        market_fit = "높음"
        summary = "귀하의 경력과 기술은 현재 시장 수요와 매우 잘 부합합니다."
    elif score >= 35:
        market_fit = "보통"
        summary = "귀하의 역량은 시장 수요와 일정 부분 부합하며 평균 수준입니다."
    else:
        market_fit = "낮음"
        summary = "현재 업종에서의 재취업 가능성은 낮은 편입니다. 기술 보완이 필요할 수 있습니다."

    return score, market_fit, summary


def generate_gpt_summary(context: str):
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "다음은 고령 근로자 통계 및 분석 점수입니다.\n이 정보를 바탕으로 사용자가 이해하기 쉽고 일관된 재취업 가능성 설명을 제공해 주세요.\n"
                "점수는 {재취업 점수}점, 시장 적합도는 '{시장 적합도}'입니다.",
            ),
            ("human", "{input}"),
        ]
    )
    structured = (
        f"{context['업종']} 업종의 전체 근로자 수는 {context['전체 근로자 수']}명이며, "
        f"{context['대상 성별']} 고령자는 {context['대상 인원']}명입니다. "
        f"점수는 {context['재취업 점수']}점이고, 시장 적합도는 '{context['시장 적합도']}'입니다."
    )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke(
        {
            "input": structured,
            "재취업 점수": context["재취업 점수"],
            "시장 적합도": context["시장 적합도"],
        }
    )


def get_final_reemployment_analysis(user_question: str):
    field, gender = extract_field_and_gender(user_question)
    stats = get_field_stats(field, gender)

    if not stats:
        return {
            "answer": "관련 데이터를 찾을 수 없습니다.",
            "reemployment_score": 0,
            "market_fit": "분석 불가",
            "summary": "해당 업종 또는 성별에 대한 분석 자료가 부족합니다.",
        }

    score, fit, summary = analyze_reemployment(field, stats, gender)

    context = {
        "업종": field,
        "전체 근로자 수": stats["total"],
        "대상 성별": gender,
        "대상 인원": stats["target"],
        "재취업 점수": score,
        "시장 적합도": fit,
    }

    answer = generate_gpt_summary(context)

    return {
        "answer": answer,
        "reemployment_score": score,
        "market_fit": fit,
        "summary": summary,
    }
