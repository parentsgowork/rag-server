from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class Bookmark(Base):
    __tablename__ = "Bookmark"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="bookmarks")

    jobId = Column(Integer, nullable=True)
    companyName = Column(String, nullable=True)
    jobTitle = Column(String, nullable=True)
    pay = Column(String, nullable=True)
    time = Column(String, nullable=True)
    location = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    registrationDate = Column(String, nullable=True)
