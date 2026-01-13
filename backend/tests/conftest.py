import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "design_engineer",
        "password": "testpassword123"
    }


@pytest.fixture
def test_project_data():
    return {
        "project_code": "PRJ-2024-001",
        "project_name": "Test Medical Device",
        "description": "Test project for unit testing",
        "product_type": "Software",
        "iec_62304_class": "B"
    }


@pytest.fixture
def test_change_data():
    return {
        "title": "Test Design Change",
        "description": "This is a test design change for unit testing",
        "change_type": "new_feature",
        "justification": "Testing purposes",
        "figma_link": "https://figma.com/test",
        "gdocs_link": "https://docs.google.com/test"
    }
