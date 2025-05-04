from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
    prompt = f"""
    정책명: {title}
    
    이 정책이 어떤 제도인지 설명해줘.
    가능하면 아래 항목별로 구분해서 설명해 줘:

    📌 대상:  
    📌 지원 요건:  
    📌 지원 내용:  
    
    정보가 부족하다면 가능한 만큼 요약해서 설명해줘.
    """
    return qa_chain.run(prompt)


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
                desc = f"'{title}'에 대한 구체적인 설명을 찾지 못했습니다. 자세한 정보는 정책 페이지를 참고해주세요."

            results.append(
                {"title": title, "description": desc, "url": policy_url_map[title]}
            )
        except Exception as e:
            print(f"[ERROR] {title} 처리 중 문제: {e}")
            continue

    return results
