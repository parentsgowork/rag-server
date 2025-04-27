from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from pinecone import Pinecone as PineconeClient
from app.core.config import settings
import os

# Pinecone 검색 -> GPT 답변 생성하는 서비스 함수

# 환경 변수 세팅
OPENAI_API_KEY = settings.OPENAI_API_KEY
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENV = settings.PINECONE_ENV
PINECONE_INDEX_NAME = settings.PINECONE_INDEX_NAME_REEMPLOYMENT  # 재취업 분석용 인덱스

# Pinecone 초기화
pinecone_client = PineconeClient(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone_client.Index(PINECONE_INDEX_NAME)

# 임베딩 모델
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 벡터 스토어
vectorstore = Pinecone.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embeddings)

# llm 세팅
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4-1106-preview")

# RetrievalQA 체인
reempolyment_qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 실제 질문을 받아 답변하는 함수
def analyze_reemployment_possibility(question: str) -> dict:
    response = reempolyment_qa_chain(question)
    return {
        "answer": response["result"],
        "sources": [doc.metadata for doc in response["source_documents"]]
    }