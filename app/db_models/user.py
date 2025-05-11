# app/db_models/user.py

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


# enum 들 정의
class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Region(str, enum.Enum):
    SEOUL = "SEOUL"
    BUSAN = "BUSAN"
    # etc...


class FinalEdu(str, enum.Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTOR = "DOCTOR"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# User 모델
class User(Base):
    __tablename__ = "User"  # ERD에 맞게 수정

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    primaryEmail = Column(String(50), unique=True)
    password = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    region = Column(Enum(Region), nullable=False)
    job = Column(String(50), nullable=False)
    career = Column(Integer, nullable=False)
    finalEdu = Column(Enum(FinalEdu), nullable=False)
    status = Column(Enum(UserStatus), nullable=False)
    role = Column(Enum(Role), nullable=True)

    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    educationInfos = relationship(
        "EducationInfo", back_populates="user", cascade="all, delete-orphan"
    )
    policyInfos = relationship(
        "PolicyInfo", back_populates="user", cascade="all, delete-orphan"
    )
