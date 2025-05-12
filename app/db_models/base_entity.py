from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime


class TimestampMixin:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
