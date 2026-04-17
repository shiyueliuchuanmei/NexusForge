"""Unit tests for quota service."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.quota import QuotaService
from app.models import User, QuotaRecord


class TestQuotaService:
    """Tests for QuotaService."""

    def test_get_current_year_month(self, db_session):
        """Test year-month format."""
        service = QuotaService(db_session)
        year_month = service.get_current_year_month()
        assert len(year_month) == 7
        assert "-" in year_month

    def test_get_or_create_quota_record_creates_new(self, db_session, test_user):
        """Test creating new quota record."""
        service = QuotaService(db_session)
        record = service.get_or_create_quota_record(test_user.id, "2024-01")

        assert record is not None
        assert record.user_id == test_user.id
        assert record.year_month == "2024-01"
        assert record.total_tokens == 0

    def test_get_or_create_quota_record_returns_existing(self, db_session, test_user):
        """Test returning existing quota record."""
        service = QuotaService(db_session)

        # Create first time
        record1 = service.get_or_create_quota_record(test_user.id, "2024-01")

        # Get second time
        record2 = service.get_or_create_quota_record(test_user.id, "2024-01")

        assert record1.id == record2.id

    def test_check_quota_within_limit(self, db_session, test_user):
        """Test quota check within limit."""
        service = QuotaService(db_session)

        # User has 1M quota, using 500k
        service.get_or_create_quota_record(test_user.id, "2024-01")
        assert service.check_quota(test_user.id, 500000) is True

    def test_check_quota_exceeds_limit(self, db_session, test_user):
        """Test quota check exceeding limit."""
        service = QuotaService(db_session)

        # User has 1M quota, trying to use 1.5M
        service.get_or_create_quota_record(test_user.id, "2024-01")
        assert service.check_quota(test_user.id, 1500000) is False

    def test_record_usage(self, db_session, test_user):
        """Test recording usage."""
        service = QuotaService(db_session)

        record = service.record_usage(
            user_id=test_user.id,
            provider="openai",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            request_type="chat"
        )

        assert record is not None
        assert record.total_tokens == 150
        assert record.provider == "openai"

        # Check quota was updated
        quota = service.get_or_create_quota_record(test_user.id, "2024-01")
        assert quota.total_tokens == 150

    def test_set_user_quota(self, db_session, test_user):
        """Test setting user quota."""
        service = QuotaService(db_session)

        user = service.set_user_quota(test_user.id, 5000000)

        assert user.monthly_token_quota == 5000000

    def test_get_user_quota_info(self, db_session, test_user):
        """Test getting user quota info."""
        service = QuotaService(db_session)

        # Record some usage
        service.record_usage(
            user_id=test_user.id,
            provider="openai",
            model="gpt-4",
            input_tokens=100,
            output_tokens=50,
            request_type="chat"
        )

        info = service.get_user_quota_info(test_user.id)

        assert info is not None
        assert info["user_id"] == test_user.id
        assert info["username"] == "test_user"
        assert info["current_month_usage"] == 150
