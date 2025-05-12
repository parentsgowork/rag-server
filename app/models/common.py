from pydantic import BaseModel
from datetime import datetime


class TimestampMixin(BaseModel):
    createdAt: datetime
    updatedAt: datetime

    class Config:
        orm_mode = True
