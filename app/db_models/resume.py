from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


# Java의 ResumeCategory enum과 동일하게 정의
class ResumeCategory(str, enum.Enum):
    GENERAL = "GENERAL"
    TECH = "TECH"
    CAREER = "CAREER"
    ACADEMIC = "ACADEMIC"


class Resume(Base):
    __tablename__ = "Resume"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False
    )  # 테이블명 수정
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    resume_category = Column(String(50), nullable=False)

    user = relationship("User", back_populates="resumes")
