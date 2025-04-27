from langchain.chains import RetrievalQA
from langchain_pinecone import Pinecone as VectorstorePinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone  # pinecone 모듈이 아니라 클래스

from app.core.config import settings
from app.utils.profile_extractor import extract_user_profile

# 환경 변수 세팅
OPENAI_API_KEY = settings.OPENAI_API_KEY
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENV = settings.PINECONE_ENV
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME_REEMPLOYMENT

# Pinecone 클라이언트 생성
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)


# 임베딩 모델
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 인덱스 객체 가져오기
index = pc.Index(settings.PINECONE_INDEX_NAME_REEMPLOYMENT)

# 벡터스토어 연결
vectorstore = VectorstorePinecone(
    index=index,
    embedding=embeddings,
    text_key="text"
)

# LLM 세팅
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4-1106-preview")

# RetrievalQA 체인
reempolyment_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 질문 처리
def analyze_reemployment_possibility(question: str) -> dict:
    response = reempolyment_qa_chain.invoke(question)
    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]]
    }

# 분석 + 프로필 추출
def analyze_and_extract_profile(question: str) -> dict:
    result = analyze_reemployment_possibility(question)
    profile = extract_user_profile(result["answer"])
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "age_group": profile.get("age_group"),
        "field": profile.get("field")
    }
