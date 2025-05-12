from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SqlEnum
from app.core.db import Base
import enum


# CodeStatus Enum
class CodeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


# AuthenticationCode 모델
class AuthenticationCode(Base):
    __tablename__ = "authentication_code"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False)
    code = Column(String, unique=True, nullable=False)
    isVerified = Column(Boolean, nullable=False)
    status = Column(SqlEnum(CodeStatus), nullable=True)
    expirationDate = Column(DateTime, nullable=False)
