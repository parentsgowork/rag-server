from sqlalchemy import create_engine, Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# BaseEntity에 해당하는 공통 필드 믹스인
class BaseEntity:
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


# 모든 모델이 상속할 Base
Base = declarative_base(cls=BaseEntity)


# DB 세션 dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
