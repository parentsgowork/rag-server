from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from sqlalchemy.orm import Session
from app.db_models.policy_info import PolicyInfo
from app.models.policySchemas import PolicySaveRequest
from app.core.config import settings

# 정책명 ↔ URL 매핑
policy_url_map = {
    "폴리텍 신중년 특화과정": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=356",
    "중장년 내일센터": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=223",
    "중장년 경력지원제": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=355",
    "재취업지원서비스 시행지원": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=180",
    "생애경력설계서비스": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=204",
    "고령자 고용지원금": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=264",
    "고령자 계속고용장려금": "https://www.moel.go.kr/policyitrd/policyItrdView.do?policy_itrd_sn=243",
}

# LangChain 세팅
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-ada-002"
)

vectorstore = PineconeVectorStore.from_existing_index(
    embedding=embeddings,
    index_name=settings.PINECONE_INDEX_NAME_POLICY,
    namespace="policy-info",
)

llm = ChatOpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
)


# 상세 설명 추출
def get_policy_description(title: str) -> str:
    fallback_hardcoded = {
        "중장년 경력지원제": """📌 대상:
- (참여자) 중장년내일센터 및 훈련기관을 통해 자격취득 또는 훈련 이수, 국민취업지원제도에 참여하여 IAP 수립 후 경력전환을 희망하는 50세 이상 중장년
- (참여기업) 고용보험 피보험자수 10인 이상 기업 (기술·경영 혁신형 중소기업은 5인 이상도 가능)

📌 지원 요건:
- 위 대상에 해당하며 경력전환을 위한 훈련 이수 또는 자격취득

📌 지원 내용:
- 주된 업무에서 퇴직한 사무직 등 중장년에게 경력전환형 일경험을
쌓을 수 있도록 지원하여 취업가능성 제고
- 참여자: 참여수당 월 150만원
- 참여기업: 참여자 1인당 월 40만원 운영지원금
- 1~3개월 유망 자격/훈련 분야 실무 수행, 직무교육, 멘토링 제공
""",
        "재취업지원서비스 시행지원": """📌 대상:
- 재취업지원서비스 지원 사업주 (300인 이상 기업)

📌 지원 요건:
- 재취업지원서비스 제도 설계 또는 운영을 준비 중인 기업

📌 지원 내용:
- 제도 설계 컨설팅, 인사담당자 교육, 업종별 표준 프로그램 개발·보급
""",
        "중장년 내일센터": """📌 대상:
- 40세 이상 중장년층에게 생애설계, 재취업 및 창업 지원, 특화서비스등의 종합 고용지원서비스를 제공하여 고용안정 및 재취업 촉진 도모

📌 지원 요건:
- 중장년층 생애설계, 재취업·창업·전직 필요자

📌 지원 내용:
- 생애경력설계, 전직스쿨, 재도약 프로그램
- 산업별 특화서비스, 중장년 청춘문화공간 운영
- 사업주 대상 고용확대 컨설팅, 직무교육, 채용지원 전담반 운영
""",
    }

    if title in fallback_hardcoded:
        return fallback_hardcoded[title]

    # 기본 프롬프트
    prompt = f"""
    정책명: {title}

    이 정책에 대한 설명을 문서에서 **그대로 인용해서** 제공해줘.
    대상, 지원 요건, 지원 내용을 항목별로 나누되, **최대한 GPT의 해석이나 요약 없이** 문서 원문 표현을 사용해줘.

    항목 예시는 다음과 같아:
    📌 대상: (원문 문장 그대로)
    📌 지원 요건: (원문 문장 그대로)
    📌 지원 내용: (원문 문장 그대로)

    정보를 직접 문서에서 발췌해서, 최대한 사실 그대로 출력해줘.
    너의 생각이나 요약 없이, 원문 중심으로 정리해줘.
    """

    result = qa_chain.run(prompt).strip()

    fallback_phrases = [
        "찾을 수 없습니다",
        "죄송합니다",
        "정보가 없습니다",
        "I don't",
        "no information",
        "모르겠습니다",
    ]

    if any(p in result for p in fallback_phrases) or len(result.split()) < 30:
        fallback_prompt = f"""
        문서에서 정책 제목이 "{title}"로 시작하는 섹션만 발췌해서 그대로 보여줘.
        다른 정책 내용은 포함하지 말고, 최대한 많이 보여줘.
        """
        result = qa_chain.run(fallback_prompt).strip()

        if any(p in result for p in fallback_phrases) or len(result.split()) < 30:
            result = "아래 링크에서 정책 원문을 확인해보세요."

    return result


# 메인 함수
def recommend_policy_by_category(category: str) -> list[dict]:
    prompt = f"""
    다음은 사용자가 관심을 가진 복지 카테고리입니다: "{category}"

    아래 리스트 중 이 카테고리에 가장 관련 있는 정책명을 1~3개 뽑아줘.

    - 재취업지원서비스 시행지원
    - 생애경력설계서비스
    - 중장년 경력지원제
    - 폴리텍 신중년 특화과정
    - 중장년 내일센터
    - 고령자 고용지원금
    - 고령자 계속고용장려금

    형식은 다음과 같이 해 줘:
    - 정책명1
    - 정책명2
    """

    raw_result = qa_chain.run(prompt)
    print("[DEBUG] LLM 응답:\n", raw_result)

    llm_titles = [
        line.strip("- ").strip()
        for line in raw_result.strip().split("\n")
        if line.strip().startswith("-")
    ]

    # 정책명 필터링
    filtered_titles = [t for t in llm_titles if t in policy_url_map]

    results = []
    for title in filtered_titles:
        try:
            desc = get_policy_description(title)

            if not desc or "I don't" in desc:
                desc = f"'{title}'에 대한 구체적인 설명을 찾지 못했습니다. 자세한 정보는 정책 링크를 참고해주세요."

            results.append(
                {"title": title, "description": desc, "url": policy_url_map[title]}
            )
        except Exception as e:
            print(f"[ERROR] {title} 처리 중 문제: {e}")
            continue

    return results


def save_policy_bookmarks(data: PolicySaveRequest, db: Session):
    for policy in data.policies:
        info = PolicyInfo(
            user_id=data.user_id,
            category=policy.category,
            title=policy.title,
            description=policy.description,
            url=policy.url,
        )
        db.add(info)
    db.commit()
    return {"message": "복지 정보 북마크 성공."}
