from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.base_entity import TimestampMixin


class Bookmark(Base, TimestampMixin):
    __tablename__ = "bookmark"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="bookmarks")

    job_id = Column(BigInteger, nullable=True)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    pay = Column(String(255), nullable=True)
    time = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    deadline = Column(String(255), nullable=True)
    registration_date = Column(String(255), nullable=True)
    detail_url = Column(String(255), nullable=True)
