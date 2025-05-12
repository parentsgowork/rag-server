from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.base_entity import TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_token"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    refresh_token = Column(String(512), nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    user = relationship(
        "User",
        back_populates="refresh_token",
        uselist=False,
    )
