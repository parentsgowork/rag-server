from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME_REEMPLOYMENT: str
    DATA_PATH_REEMPLOYMENT_ANALYSIS: str
    PINECONE_INDEX_NAME_POLICY: str
    DATA_PATH_POLICY_PDF: str
    seoul_openapi_key: str
    seoul_openapi_url: str

    JOB_INFO_URL: str
    JOB_INFO_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
