import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

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
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    client.post("/users/", json={"username": "admin1", "email": "admin@test.com", "password": "admin123", "role": "admin"})
    res = client.post("/users/login", data={"username": "admin1", "password": "admin123"})
    return res.json()["access_token"]

@pytest.fixture
def author_token(client):
    client.post("/users/", json={"username": "author1", "email": "author@test.com", "password": "author123", "role": "author"})
    res = client.post("/users/login", data={"username": "author1", "password": "author123"})
    return res.json()["access_token"]

@pytest.fixture
def reader_token(client):
    client.post("/users/", json={"username": "reader1", "email": "reader@test.com", "password": "reader123", "role": "reader"})
    res = client.post("/users/login", data={"username": "reader1", "password": "reader123"})
    return res.json()["access_token"]
