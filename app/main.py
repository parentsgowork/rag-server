# fast api 앱 실행 파일
from fastapi import FastAPI
from app.api import routes
from app.core.db import engine
from app.db_models.education import EducationInfo
from app.db_models.user import User  # 새로 만들 예정
from app.core.db import Base


app = FastAPI(title="RAG Chatbot API", description="RAG 챗봇 API", version="0.1.0")

# 라우터 등록
app.include_router(routes.router)


# root test endpoint
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API"}


# 현재 연결된 DB 테이블 초기 생성,반영
Base.metadata.create_all(bind=engine)
