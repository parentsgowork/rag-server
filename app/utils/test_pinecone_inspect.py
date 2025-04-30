from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import numpy as np
import os
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()

# 환경 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME_REEMPLOYMENT")

# Pinecone 연결
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pc.Index(PINECONE_INDEX_NAME)

# [1] 인덱스 상태 출력
print("\n📊 [1] describe_index_stats() 결과:")
print(index.describe_index_stats())

# [2] 쿼리 임베딩 생성 확인
print("\n🧪 [2] embed_query() 테스트:")
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
query_text = "제조업 업종의 55세 이상 여성 근로자 수는 얼마나 되나요?"
vec = embeddings.embed_query(query_text)
print(f"   👉 벡터 길이: {len(vec)}")
print(f"   👉 벡터 앞 5개: {vec[:5]}")

# [3] 유사도 검색 테스트
print("\n🔍 [3] similarity_search() 테스트:")
vectorstore = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")
docs = vectorstore.similarity_search(query_text, k=5)
if not docs:
    print("   ❌ 검색 결과 없음")
else:
    for i, doc in enumerate(docs):
        print(f"\n   [{i+1}] {doc.page_content[:200]}...")
        print(f"        🏷 metadata: {doc.metadata}")

# [4] 특정 ID의 벡터값 확인 (예: 3, 4, 5)
print("\n📦 [4] Pinecone 벡터 fetch 테스트 (ID 3~5):")
response = index.fetch(ids=["3", "4", "5"])
for rec_id, record in response.vectors.items():
    values = record["values"]
    is_zero = np.allclose(values, 0.0)
    print(f"   🔹 ID: {rec_id} → 길이: {len(values)}, 제로 벡터?: {'✅' if is_zero else '❌'}")
    print(f"      앞 5개 값: {values[:5]}")
