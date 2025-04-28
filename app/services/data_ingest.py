import os
import pandas as pd
from dotenv import load_dotenv
import openai
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from openai import OpenAI

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

print("인덱스 생성 완료:", pc.list_indexes().names())

# 인덱스 객체 가져오기
index = pc.Index(index_name)

# CSV 로드 함수
def load_clean_dataframe(file_path):
    df_raw = pd.read_csv(file_path, encoding="cp949", header=None)
    df = df_raw[2:].reset_index(drop=True)
    df.columns = df_raw.iloc[1].values
    return df

# OpenAI GPT 요약 함수
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def summarize_row(metadata: dict) -> str:
    prompt = f"""
        당신은 55세 이상 근로자 재취업 가능성 분석을 돕는 AI입니다.

        다음 업종 데이터를 기반으로, 50대 이상 여성 근로자 수와 전체 근로자 수를 참고하여,
        업종 특성과 재취업 가능성에 대해 자연어로 간결하고 친절하게 요약해 주세요.

        [업종]: {metadata.get('구분별(2)')}
        [전체 근로자 수]: {metadata.get('전체 근로자 (명)')}
        [55세 이상 근로자 수]: {metadata.get('55세 이상 근로자 (명)')}
        [55세 이상 남성 근로자 수]: {metadata.get('55세 이상 남성근로자 (명)')}
        [55세 이상 여성 근로자 수]: {metadata.get('55세 이상 여성근로자 (명)')}

        가능하면 "업종명은 50대 이상 여성 근로자가 약 X명 존재하며, 재취업 가능성이 높습니다" 처럼 작성해 주세요.
"""
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# 텍스트 -> 벡터 변환 함수
def text_to_vector(text):
    if not text.strip():
        print("빈 문자열 발견:", text)
        return None
    try:
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"OpenAI 임베딩 실패: {e}")
        return None

# 업로드 함수
def ingest_data(file_path):
    df = load_clean_dataframe(file_path)
    print("테이블 열 이름:", df.columns.tolist())
    print("테이블 처음 3행:\n", df.head(3))

    vectors = []
    for i, row in df.iterrows():
        metadata = {str(col): str(val) for col, val in zip(df.columns, row)}

        try:
            text = summarize_row(metadata)
        except Exception as e:
            print(f"GPT 요약 실패 (row {i}): {e}")
            continue

        vector = text_to_vector(text)
        if vector is None:
            print(f"벡터 생성 실패: row {i}")
            continue

        metadata["text"] = text
        vectors.append((str(i), vector, metadata))

    print("생성된 벡터 개수:", len(vectors))

    if not vectors:
        print("업로드할 벡터가 없습니다. 종료합니다.")
        return

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        print(f"업로드 중... {i} ~ {i + batch_size}개")
        index.upsert(vectors=vectors[i:i + batch_size], namespace="default")

    print("모든 데이터 업로드 완료")
    stats = index.describe_index_stats()
    print("인덱스 통계:", stats)

# 실행
if __name__ == "__main__":
    ingest_data(file_path)
