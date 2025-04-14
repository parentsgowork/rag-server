# dotenv 읽기 및 설정 관리
# app/core/config.py

from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME: str
    DATA_PATH:str

    class Config:
        env_file = ".env"

settings = Settings()
