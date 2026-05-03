import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try: yield db
    finally: db.close(); Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db(): yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(): return {"username": "testuser", "email": "test@example.com", "password": "TestPass123!"}

@pytest.fixture
def auth_token(client, test_user, db_session):
    client.post("/api/auth/register", json=test_user)
    resp = client.post("/api/auth/login", data={"username": test_user["username"], "password": test_user["password"]})
    return resp.json()["access_token"]