# fast api 앱 실행 파일
from fastapi import FastAPI
from app.api import routes

app = FastAPI(
    title="RAG Chatbot API",
    description="RAG 챗봇 API",
    version="0.1.0"
)

# 라우터 등록
app.include_router(routes.router)

# root test endpoint
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot API"}
