import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.models import Base, User, ShortUrl
from dependencies.dependencies import get_session
from routes.shortener_routes import shortener_router
from routes.user_routes import user_router
from routes.metrics_routes import metrics_router
from utils.short_code import generate_short_id
from auth.auth import bcrypt_hash, create_access_token


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, expire_on_commit=False)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def app(db_session):
    app = FastAPI()
    app.include_router(shortener_router)
    app.include_router(metrics_router)
    app.include_router(user_router)

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def test_user(db_session):
    user = User(
        name="Test User",
        email="test@example.com",
        password=bcrypt_hash.hash("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user(db_session):
    user = User(
        name="Other User",
        email="other@example.com",
        password=bcrypt_hash.hash("password456"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_auth_headers(other_user):
    token = create_access_token({"sub": other_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def short_url(db_session, test_user):
    short = ShortUrl(
        origin_url="https://example.com",
        hash_url=generate_short_id(),
        user_id=test_user.id,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db_session.add(short)
    db_session.commit()
    db_session.refresh(short)
    return short


@pytest.fixture
def expired_short_url(db_session, test_user):
    short = ShortUrl(
        origin_url="https://expired.com",
        hash_url=generate_short_id(),
        user_id=test_user.id,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(short)
    db_session.commit()
    db_session.refresh(short)
    return short


@pytest.fixture
def anonymous_short_url(db_session):
    short = ShortUrl(
        origin_url="https://anon.com",
        hash_url=generate_short_id(),
        user_id=None,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db_session.add(short)
    db_session.commit()
    db_session.refresh(short)
    return short
