from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.base_entity import TimestampMixin


class EducationInfo(Base, TimestampMixin):
    __tablename__ = "education_info"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="education_infos")

    title = Column(String(50), nullable=False)
    url = Column(Text, nullable=True)
