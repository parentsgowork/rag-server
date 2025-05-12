from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class EducationInfo(Base):
    __tablename__ = "EducationInfo"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="educationInfos")

    title = Column(String(50), nullable=False)
    url = Column(Text, nullable=True)
