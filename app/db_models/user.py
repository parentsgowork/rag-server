from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum
from app.db_models.refresh_token import RefreshToken
from app.db_models.base_entity import TimestampMixin

# ------------------ ENUM 정의 ------------------


class gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class region(str, enum.Enum):
    SEOUL = "SEOUL"
    GYEONGGI = "GYEONGGI"
    INCHEON = "INCHEON"
    GANGWON = "GANGWON"
    DAEJEON = "DAEJEON"
    SEJONG = "SEJONG"
    CHUNGBUK = "CHUNGBUK"


class final_edu(str, enum.Enum):
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


class status(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


# ------------------ User 모델 정의 ------------------


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    primary_email = Column(String(50), unique=True)
    password = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(SqlEnum(gender), nullable=False)
    region = Column(SqlEnum(region), nullable=False)
    job = Column(String(50), nullable=False)
    career = Column(Integer, nullable=False)
    final_edu = Column(SqlEnum(final_edu), nullable=False)
    status = Column(SqlEnum(status), nullable=False)
    role = Column(SqlEnum(role), nullable=True)

    refresh_token_id = Column(Integer, ForeignKey("refresh_token.id"), nullable=True)

    refreshToken = relationship(
        "RefreshToken",
        back_populates="user",
        uselist=False,
        foreign_keys=[refresh_token_id],
        primaryjoin="User.refresh_token_id==RefreshToken.id",
    )

    bookmarks = relationship(
        "Bookmark", back_populates="user", cascade="all, delete-orphan"
    )
    policyInfos = relationship(
        "PolicyInfo", back_populates="user", cascade="all, delete-orphan"
    )
    educationInfos = relationship(
        "EducationInfo", back_populates="user", cascade="all, delete-orphan"
    )
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
