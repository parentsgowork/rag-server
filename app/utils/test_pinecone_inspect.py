from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from app.core.config import settings

# Pinecone 연결
pc = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
index = pc.Index(settings.PINECONE_INDEX_NAME_REEMPLOYMENT)

# OpenAI 임베딩 모델 (저장할 때와 동일한 모델 써야 함!)
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY,
    model="text-embedding-ada-002",  # ✅ data_ingest와 반드시 동일
)

# 벡터스토어 설정
vectorstore = PineconeVectorStore(
    index=index, embedding=embeddings, namespace="default"
)

# 1. 인덱스 상태 출력
print("\n[1] describe_index_stats() 결과:")
stats = index.describe_index_stats()
print(stats)

# 2. 쿼리 임베딩 벡터 확인
query = "제조업 업종의 55세 이상 여성 근로자 수는 몇 명인가요?"
print("\n embed_query() 테스트:")
embedded = embeddings.embed_query(query)
print(f"   벡터 길이: {len(embedded)}")
print(f"   벡터 앞 5개: {embedded[:5]}")

# 3. 벡터 유사도 검색 수행
print("\n [3] similarity_search() 테스트:")
results = vectorstore.similarity_search(query, k=5)
if not results:
    print("   ❌ 검색 결과 없음")
else:
    print(f"   ✅ 검색 결과 {len(results)}건:")
    for i, doc in enumerate(results):
        print(f"\n[{i+1}] {doc.page_content[:300]}...")
        print(f"     🏷 metadata: {doc.metadata}")
