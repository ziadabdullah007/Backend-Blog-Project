import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.setdefault("REDIS_HOST", "127.0.0.1")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


TEST_DB_PATH = Path("test.db")
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def client():
    return TestClient(app)


def _register_and_login(client: TestClient, username: str, email: str, password: str, role: str) -> str:
    register_res = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "role": role,
        },
    )
    assert register_res.status_code == 201

    login_res = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert login_res.status_code == 200
    return login_res.json()["access_token"]


@pytest.fixture
def admin_token(client):
    return _register_and_login(client, "admin1", "admin@test.com", "admin123", "admin")


@pytest.fixture
def author_token(client):
    return _register_and_login(client, "author1", "author@test.com", "author123", "author")


@pytest.fixture
def reader_token(client):
    return _register_and_login(client, "reader1", "reader@test.com", "reader123", "reader")
