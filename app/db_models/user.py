from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.db_models.refresh_token import RefreshToken
from app.db_models.base_entity import TimestampMixin
import enum


# ENUM 정의
class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Region(str, enum.Enum):
    SEOUL = "SEOUL"
    GYEONGGI = "GYEONGGI"
    INCHEON = "INCHEON"
    GANGWON = "GANGWON"
    DAEJEON = "DAEJEON"
    SEJONG = "SEJONG"
    CHUNGBUK = "CHUNGBUK"


class FinalEdu(str, enum.Enum):
    HIGH_SCHOOL = "HIGH_SCHOOL"
    ASSOCIATE = "ASSOCIATE"
    BACHELOR = "BACHELOR"
    MASTER = "MASTER"
    DOCTOR = "DOCTOR"

    @property
    def description(self):
        return {
            "HIGH_SCHOOL": "고등학교 졸업",
            "ASSOCIATE": "전문대학 졸업",
            "BACHELOR": "대학교 졸업",
            "MASTER": "석사 학위",
            "DOCTOR": "박사 학위",
        }[self.value]


class Status(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# User 모델
class User(Base, TimestampMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    primary_email = Column(String(50), unique=True)
    password = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(SqlEnum(Gender), nullable=False)
    region = Column(SqlEnum(Region), nullable=False)
    job = Column(String(50), nullable=False)
    career = Column(Integer, nullable=False)
    final_edu = Column(SqlEnum(FinalEdu), nullable=False)
    status = Column(SqlEnum(Status), nullable=False)
    role = Column(SqlEnum(Role), nullable=True)

    refresh_token_id = Column(Integer, ForeignKey("refresh_token.id"), nullable=True)

    refresh_token = relationship("RefreshToken", back_populates="user", uselist=False)

    bookmarks = relationship(
        "Bookmark", back_populates="user", cascade="all, delete-orphan"
    )
    policy_infos = relationship(
        "PolicyInfo", back_populates="user", cascade="all, delete-orphan"
    )

    education_infos = relationship(
        "EducationInfo", back_populates="user", cascade="all, delete-orphan"
    )
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
