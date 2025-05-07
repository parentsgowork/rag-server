from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class PolicyInfo(Base):
    __tablename__ = "policy_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)

    user = relationship("User", back_populates="policyInfos")
