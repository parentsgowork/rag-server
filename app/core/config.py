from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings
import base64

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME_REEMPLOYMENT: str

    PINECONE_INDEX_NAME_POLICY: str

    seoul_openapi_key: str
    seoul_openapi_url: str

    JOB_INFO_URL: str
    JOB_INFO_KEY: str
    DATABASE_URL: str

    JWT_SECRET_KEY_BASE64: str
    JWT_ALGORITHM: str = "HS256"

    # ✅ Base64 디코딩된 JWT secret 키
    @property
    def jwt_secret_bytes(self) -> bytes:
        return base64.b64decode(self.JWT_SECRET_KEY_BASE64)

    class Config:
        env_file = ".env"

    class Config:
        env_file = ".env"


settings = Settings()
