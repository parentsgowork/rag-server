import os
import pandas as pd
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.core.config import settings

# .env 환경 변수 로드
load_dotenv()

# 설정값
index_name = settings.PINECONE_INDEX_NAME_REEMPLOYMENT
file_path = settings.DATA_PATH_REEMPLOYMENT_ANALYSIS

# Pinecone 초기화 및 기존 인덱스 삭제 후 재생성
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)
pc.create_index(
    name=index_name,
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)
print("✅ Pinecone 인덱스 생성 완료:", index_name)


# CSV 로드 함수 (두 번째 줄을 헤더로 사용)
def load_clean_dataframe(file_path):
    df = pd.read_csv(file_path, encoding="cp949", header=1)
    return df


# 데이터 적재 함수
def ingest_data(file_path):
    df = load_clean_dataframe(file_path)
    print("📊 테이블 열:", df.columns.tolist())
    print("📌 샘플 데이터:", df.head(2))

    documents = []
    for i, row in df.iterrows():
        text = (
            f"{row['구분별(2)']} 업종의 사업장 수는 {row['사업장 (개)']}개이고, "
            f"전체 근로자 수는 {row['전체 근로자 (명)']}명입니다. "
            f"55세 이상 근로자는 {row['55세 이상 근로자 (명)']}명이며, "
            f"이 중 남성은 {row['55세 이상 남성근로자 (명)']}명, 여성은 {row['55세 이상 여성근로자 (명)']}명입니다."
        )
        metadata = {"field": str(row["구분별(2)"]), "age_group": "55세 이상"}
        documents.append(Document(page_content=text, metadata=metadata))

    print(f"벡터로 변환할 문서 수: {len(documents)}")

    # 임베딩 모델 명시적으로 지정 (OpenAI)
    embedding = OpenAIEmbeddings(
        openai_api_key=settings.OPENAI_API_KEY, model="text-embedding-ada-002"
    )

    # 벡터스토어로 업로드
    vectorstore = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embedding,
        index_name=index_name,
        namespace="default",
    )
    print("✅ 벡터 업로드 완료")

    stats = pc.Index(index_name).describe_index_stats()
    print("인덱스 상태:", stats)


if __name__ == "__main__":
    ingest_data(file_path)
