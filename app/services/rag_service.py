from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_pinecone import Pinecone as VectorstorePinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone

from app.core.config import settings
from app.utils.profile_extractor import extract_user_profile

# 설정값
OPENAI_API_KEY = settings.OPENAI_API_KEY
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENV = settings.PINECONE_ENV
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME_REEMPLOYMENT

# Pinecone 연결
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
vectorstore = VectorstorePinecone(index=index, embedding=embeddings, text_key="text")

# LLM
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4-1106-preview")

# Prompt
prompt_template = PromptTemplate.from_template("""
당신은 사용자의 재취업 가능성을 객관적인 수치 데이터로 간결하게 요약하는 AI입니다.

다음 context(문서)와 사용자 질문(question)을 참고하여 다음 규칙에 따라 답변하세요:

- **55세 이상 남성/여성 근로자 수**와 **전체 근로자 대비 비율(%)**을 명시합니다.
- **감성적 표현 없이** 객관적 수치 기반으로만 답합니다.
- 2~3줄 이내로 요약합니다.
- 추가 분석, 조언, 추천은 쓰지 않습니다.

<context>
{context}
</context>

질문: {question}
""")

# RetrievalQA 체인
reempolyment_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt_template},
    return_source_documents=True,
    input_key="question"  # ✅ "question"으로 바꿈
)

# 함수
def analyze_reemployment_possibility(question: str) -> dict:
    response = reempolyment_qa_chain.invoke({"question": question})  # ✅ "question"으로 보냄
    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]]
    }

def analyze_and_extract_profile(question: str) -> dict:
    result = analyze_reemployment_possibility(question)
    profile = extract_user_profile(result["answer"])
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "age_group": profile.get("age_group"),
        "field": profile.get("field")
    }
