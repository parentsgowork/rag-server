from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base
from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "RefreshToken"

    id = Column(Integer, primary_key=True, index=True)

    refreshToken = Column(String(512), nullable=False)

    expiryDate = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="refreshToken", uselist=False)
