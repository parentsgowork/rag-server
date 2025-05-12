from sqlalchemy import Column, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.base_entity import TimestampMixin


class PolicyInfo(Base, TimestampMixin):
    __tablename__ = "policy_info"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="policy_infos")

    title = Column(String(50), nullable=False)
    category = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
