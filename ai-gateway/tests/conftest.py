"""Test configuration and fixtures."""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import User, UsageRecord, QuotaRecord


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="test_user",
        api_key="sk-test-api-key-12345",
        monthly_token_quota=1000000,
        is_active=1
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def mock_adapter():
    """Create a mock adapter for testing."""
    adapter = MagicMock()
    adapter.provider_name = "mock"
    adapter.generate_text.return_value = MagicMock(
        content="Test response",
        model="gpt-4",
        input_tokens=100,
        output_tokens=50,
        finish_reason="stop",
        raw_response={"id": "test-123"}
    )
    adapter.generate_image.return_value = [
        MagicMock(url="https://example.com/image.png")
    ]
    return adapter
