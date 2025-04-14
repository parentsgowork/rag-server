import os
import csv
from dotenv import load_dotenv
import openai
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

# .env 파일 로드
load_dotenv()

# 환경 변수 설정
openai.api_key = settings.OPENAI_API_KEY

# 데이터 경로 설정
file_path=settings.DATA_PATH

# Pinecone 인스턴스 생성 (API Key와 같은 환경 값 설정)
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY,
    environment=settings.PINECONE_ENV
)

# 기존 인덱스를 삭제하고 새 인덱스를 생성 (차원 1536)
if settings.PINECONE_INDEX_NAME in pc.list_indexes().names():
    pc.delete_index(settings.PINECONE_INDEX_NAME)

# 새 Pinecone 인덱스 생성
pc.create_index(
    name=settings.PINECONE_INDEX_NAME, # 인덱스 이름
    dimension=1536, # 벡터 차원 수 (OpenAI의 text-embedding-ada-002 모델은 1536 차원)
    metric='cosine', # 벡터 간 유사도 계산 방식 -> 코사인
    spec=ServerlessSpec( # 서버리스 환경 설정정
        cloud='aws',
        region='us-east-1'
    )
)

# 생성 확인용 인덱스 목록 출력
print(pc.list_indexes())

# 생성할 인덱스 객체 가져오기 
#n namepspace는 같은 인덱스 내 데이터를 구분할 때 사용 (여기선 비워둠)
index = pc.Index(settings.PINECONE_INDEX_NAME)

# CSV 데이터 로드 함수
def load_csv_data(file_path):
    data = [] # 데이터 저장 인덱스
    # csv 파일 열기 
    with open(file_path, 'r', encoding='cp949') as file:
        reader = csv.reader(file)
        next(reader) # 첫번째 줄 (헤더)는 건너뜀뜀
        for row in reader:
            data.append(row)
    return data

# 텍스트 → 벡터 변환 함수
def text_to_vector(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


# 데이터 업로드
def ingest_data(file_path):
    # csv 파일에서 데이터 읽어오기
    data = load_csv_data(file_path)
    vectors = [] # 업로드할 벡터데이터를 저장할 리스트트

    # 데이터 한 줄씩 읽어서 벡터로 변환 + medatadata 설정정
    for i, row in enumerate(data):
       
        text = row[1]  # 교육명 기준으로 임베딩 (row[0]: 번호)
        vector = text_to_vector(text) # 텍스트 -> 벡터 변환환

        # metadata 추가
        metadata = {
            "번호": row[0],
            "교육명": row[1],
            "교육기간": row[2],
            "교육장소": row[3],
            "모집정원": row[4],
            "신청방법": row[5],
            "문의처": row[6],
            "교육비용":row[7],
            "교육상태":row[8],
            "강좌상세화면":row[9]
        }

        # 벡터 데이터 구성
        # (id, 벡터값, metadata)
        vectors.append((str(i), vector, metadata))  # metadata 추가

    # 업로드 배치 단위 설정 (100개씩 업로드)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        # pinecone에 인덱스 데이터 업로드
        index.upsert(
            vectors=vectors[i:i+batch_size],
            namespace=""
        )
        print(f"{i} ~ {i+batch_size} 업로드 완료")

    print("모든 데이터 업로드 완료")


# 실행
if __name__ == "__main__":
    ingest_data(file_path)
    print(index.describe_index_stats())
