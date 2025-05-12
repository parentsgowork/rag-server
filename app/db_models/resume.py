from sqlalchemy import Column, BigInteger, String, Text, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.base_entity import TimestampMixin
import enum


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


class Resume(Base, TimestampMixin):
    __tablename__ = "resume"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="resumes")

    title = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    resume_category = Column(SqlEnum(ResumeCategory), nullable=False)
