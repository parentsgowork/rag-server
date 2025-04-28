from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone

from app.core.config import settings

# 설정값
OPENAI_API_KEY = settings.OPENAI_API_KEY
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENV = settings.PINECONE_ENV
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME_REEMPLOYMENT

# Pinecone 연결
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pc.Index(PINECONE_INDEX_NAME)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    text_key="text"
)

# LLM 연결
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4-1106-preview"
)

# Prompt 템플릿
prompt_template = PromptTemplate.from_template("""
당신은 제공된 context(문서)만을 사용하여 객관적인 수치 정보를 요약하는 재취업 분석 AI입니다.

반드시 다음 정보를 찾아야 합니다:
- 55세 이상 전체 근로자 수 (명)
- 55세 이상 여성 근로자 수 (명)
- 55세 이상 남성 근로자 수 (명)
- 전체 근로자 수 대비 55세 이상 여성 비율 (%)
- 전체 근로자 수 대비 55세 이상 남성 비율 (%)

**계산 방법**:
- 여성 비율 = (55세 이상 여성 근로자 수 / 전체 근로자 수) * 100
- 남성 비율 = (55세 이상 남성 근로자 수 / 전체 근로자 수) * 100

규칙:
- 문서(context)에 없는 정보는 "알 수 없음"으로 답하세요.
- 감성적인 표현 없이, 수치 기반으로 간결히 답하세요.
- 2~3줄 이내로 요약하세요.

<context>
{context}
</context>

질문: {question}

답변 형식 예시:
- 업종별: 부동산업
- 55세 이상 전체 근로자: 27503명
- 55세 이상 여성 근로자: 11022명
- 55세 이상 남성 근로자: 16481명
- 전체 근로자 대비 55세 이상 여성 비율: 21.7%
- 전체 근로자 대비 55세 이상 남성 비율: 27.4%
""")

# 유저 프로필 추출
def extract_user_profile(text: str) -> dict:
    field_candidates = ["부동산업", "부동산", "농업", "제조업", "서비스업", "건설업", "정보통신업", "금융업", "교육서비스업"]
    gender_candidates = {"여성": "여성", "여자": "여성", "남성": "남성", "남자": "남성"}

    detected_field = None
    for f in field_candidates:
        if f in text:
            detected_field = f
            break

    detected_gender = None
    for key, value in gender_candidates.items():
        if key in text:
            detected_gender = value
            break

    return {
        "field": detected_field,
        "gender": detected_gender or "여성"  # 기본 여성
    }

# 재취업 분석 메인 함수
def analyze_reemployment_possibility(question: str) -> dict:
    profile = extract_user_profile(question)
    field = profile.get("field", "")
    gender = profile.get("gender", "여성")

    # 필터 설정
    filter_query = {}
    if field:
        filter_query["구분별(2)"] = {"$contains": field}

    # 1차 필터 검색
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1, "filter": filter_query or None})
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True,
        input_key="question"
    )
    response = chain.invoke({"question": question})

    # 2차 fallback (필터 없이)
    if not response.get("source_documents"):
        retriever_fallback = vectorstore.as_retriever(search_kwargs={"k": 1})
        chain_fallback = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever_fallback,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True,
            input_key="question"
        )
        response = chain_fallback.invoke({"question": question})

    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]],
        "field": field,
        "gender": gender
    }

# 최종 API 포맷팅
def get_final_reemployment_analysis(question: str) -> dict:
    result = analyze_reemployment_possibility(question)
    answer_text = result["answer"]
    field = result["field"] or "해당 업종"
    gender = result["gender"] or "여성"

    final_message = f"고객님과 비슷한 {field} 분야 {gender} 종사자의 재취업 정보입니다:\n\n{answer_text}"

    return {
        "message": final_message,
        "sources": result["sources"]
    }
