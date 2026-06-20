from sqlalchemy import String, create_engine, Column, Integer, ForeignKey, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import declarative_base, relationship
from enum import Enum
from datetime import datetime


db = create_engine("sqlite:///banco.db")
Base = declarative_base()

class AccessLevel(str, Enum):
    SUB = "subscriber"
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False,unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    access = Column(SqlEnum(AccessLevel), default=AccessLevel.USER)

    short_urls = relationship("ShortUrl", back_populates="user", cascade="all, delete-orphan")

    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.access = AccessLevel.USER


class ShortUrl(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    origin_url = Column(String, nullable=False)
    hash_url = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="short_urls")
    metrics = relationship("UrlMetric", back_populates="short_url", cascade="all, delete-orphan")

    def __init__(self, origin_url, hash_url, user_id=None, expires_at=None):
        self.origin_url = origin_url
        self.hash_url = hash_url
        self.user_id = user_id
        self.expires_at = expires_at or datetime.utcnow()


class UrlMetric(Base):
    __tablename__ = "url_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)

    short_url_id = Column(Integer, ForeignKey("short_urls.id"), nullable=False)
    short_url = relationship("ShortUrl", back_populates="metrics")
        

