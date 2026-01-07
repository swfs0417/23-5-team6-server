import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings
from asset_management.database import import_models
from asset_management.database.common import Base
from asset_management.main import app
from asset_management.database.session import get_session

import_models()

# Use SQLite in-memory database for testing instead of MySQL
TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override"""
    TestingSessionLocal = sessionmaker(
        bind=test_db, autocommit=False, autoflush=False, future=True
    )
    
    def override_get_session():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session(test_db):
    """Provide a database session for verification"""
    TestingSessionLocal = sessionmaker(
        bind=test_db, autocommit=False, autoflush=False, future=True
    )
    return TestingSessionLocal

# 환경 변수로 설정된 환경을 가져옵니다.
ENV = "test"

class Settings(BaseSettings):
    @property
    def is_local(self) -> bool:
        return ENV == "local"
    
    @property
    def is_test(self) -> bool:
        return ENV == "test"

    @property
    def is_prod(self) -> bool:
        return ENV == "prod"

    @property
    def env_file(self) -> str:
        return f".env.{ENV}"


SETTINGS = Settings()