# fast api 앱 실행 파일
from fastapi import FastAPI
from app.api import routes
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import engine
from app.db_models.education_info import EducationInfo
from app.db_models.user import User  # 새로 만들 예정
from app.core.db import Base


app = FastAPI(title="RAG Chatbot API", description="RAG 챗봇 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://parentsgowork.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(routes.router)


# root test endpoint
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API"}
