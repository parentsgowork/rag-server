from sqlalchemy import Column, Integer, String, Text, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


# ------------------ ResumeCategory Enum ------------------


class ResumeCategory(str, enum.Enum):
    GROWTH = "GROWTH"
    MOTIVATION = "MOTIVATION"
    ASPIRATION = "ASPIRATION"
    STRENGTH = "STRENGTH"
    PROJECT_EXPERIENCE = "PROJECT_EXPERIENCE"

    @property
    def display_name(self):
        return {
            "GROWTH": "성장과정",
            "MOTIVATION": "지원동기",
            "ASPIRATION": "입사포부",
            "STRENGTH": "강점약점",
            "PROJECT_EXPERIENCE": "프로젝트경험",
        }[self.value]


# ------------------ Resume 모델 ------------------


class Resume(Base):
    __tablename__ = "Resume"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="resumes")

    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)

    resumeCategory = Column(SqlEnum(ResumeCategory), nullable=False)
