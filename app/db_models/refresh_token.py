from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String(512), nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    user = relationship(
        "User",
        back_populates="refreshToken",
        uselist=False,
        primaryjoin="RefreshToken.id==User.refresh_token_id",
    )
