from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class EducationInfo(Base):
    __tablename__ = "education_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="educationInfos")

    title = Column(String(50), nullable=False)
    url = Column(Text, nullable=True)
