from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.db import Base
from sqlalchemy.orm import relationship


class EducationInfo(Base):
    __tablename__ = "EducationInfo"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)

    user = relationship("User", back_populates="educationInfos")
