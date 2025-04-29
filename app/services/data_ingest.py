import os
import pandas as pd
from dotenv import load_dotenv
import openai
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

# .env 파일 로드
load_dotenv()

# 환경 변수 설정
openai.api_key = settings.OPENAI_API_KEY
index_name = settings.PINECONE_INDEX_NAME_REEMPLOYMENT
file_path = settings.DATA_PATH_REEMPLOYMENT_ANALYSIS

# Pinecone 초기화
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# 기존 인덱스 삭제 후 새로 생성
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

pc.create_index(
    name=index_name,
    dimension=1536,
    metric='cosine',
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)

print("✅ 인덱스 생성 완료:", pc.list_indexes().names())

# 인덱스 객체 가져오기
index = pc.Index(index_name)

# CSV 로드 함수 (두 번째 줄을 컬럼으로 사용)
def load_clean_dataframe(file_path):
    df = pd.read_csv(file_path, encoding="cp949", header=1)
    return df

# 텍스트 → 벡터 변환
def text_to_vector(text):
    if not text.strip():
        print("빈 문자열 발견:", text)
        return None
    try:
        resp = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"❌ OpenAI 임베딩 실패: {e}")
        return None

# 데이터 업로드 함수
def ingest_data(file_path):
    df = load_clean_dataframe(file_path)
    print("테이블 열 이름:", df.columns.tolist())
    print("(테스트) 테이블 처음 3행:\n", df.head(3))

    vectors = []
    for i, row in df.iterrows():
        # 자연어 스타일 텍스트 생성
        text = (
            f"{row['구분별(2)']} 업종의 사업장 수는 {row['사업장 (개)']}개이고, "
            f"전체 근로자 수는 {row['전체 근로자 (명)']}명입니다. "
            f"55세 이상 근로자는 {row['55세 이상 근로자 (명)']}명이며, "
            f"이 중 남성은 {row['55세 이상 남성근로자 (명)']}명, 여성은 {row['55세 이상 여성근로자 (명)']}명입니다."
        )

        vector = text_to_vector(text)
        if vector is None:
            continue

        metadata = {
            "field": str(row['구분별(2)']),
            "age_group": "55세 이상",
            "text": text
        }

        vectors.append((str(i), vector, metadata))

    print(f"생성된 벡터 개수: {len(vectors)}")

    if not vectors:
        print("업로드할 벡터가 없습니다. 종료합니다.")
        return

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        chunk = vectors[i: i + batch_size]
        print(f"⬆️ 업로드 중... {i} ~ {i + len(chunk)}개")
        index.upsert(vectors=chunk, namespace="default")

    print("🎉 모든 데이터 업로드 완료!")
    stats = index.describe_index_stats()
    print("📊 인덱스 통계:", stats)

if __name__ == "__main__":
    ingest_data(file_path)
