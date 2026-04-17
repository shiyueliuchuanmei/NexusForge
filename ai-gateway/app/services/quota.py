"""Quota service for managing user token quotas and usage tracking."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models import User, UsageRecord, QuotaRecord


class QuotaService:
    """Service for managing user quotas and usage records."""

    def __init__(self, db: Session):
        self.db = db

    def get_current_year_month(self) -> str:
        """Get current year-month string."""
        return datetime.utcnow().strftime("%Y-%m")

    def get_or_create_quota_record(self, user_id: int, year_month: str) -> QuotaRecord:
        """Get or create a quota record for user and month."""
        record = self.db.query(QuotaRecord).filter(
            QuotaRecord.user_id == user_id,
            QuotaRecord.year_month == year_month
        ).first()

        if not record:
            user = self.db.query(User).filter(User.id == user_id).first()
            record = QuotaRecord(
                user_id=user_id,
                year_month=year_month,
                total_tokens=0,
                quota_limit=user.monthly_token_quota if user else 0
            )
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)

        return record

    def check_quota(self, user_id: int, required_tokens: int) -> bool:
        """Check if user has enough quota for the requested tokens."""
        year_month = self.get_current_year_month()
        quota_record = self.get_or_create_quota_record(user_id, year_month)
        return (quota_record.total_tokens + required_tokens) <= quota_record.quota_limit

    def record_usage(
        self,
        user_id: int,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_type: str,
        request_params: str = None,
        response_data: str = None
    ) -> UsageRecord:
        """Record usage and update quota totals."""
        year_month = self.get_current_year_month()

        # Create usage record
        usage_record = UsageRecord(
            user_id=user_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            request_type=request_type,
            request_params=request_params,
            response_data=response_data
        )
        self.db.add(usage_record)

        # Update quota record
        quota_record = self.get_or_create_quota_record(user_id, year_month)
        quota_record.total_tokens += input_tokens + output_tokens

        self.db.commit()
        self.db.refresh(usage_record)
        return usage_record

    def get_user_usage_stats(
        self,
        user_id: int,
        year_month: Optional[str] = None
    ) -> dict:
        """Get usage statistics for a user."""
        if year_month is None:
            year_month = self.get_current_year_month()

        stats = self.db.query(
            func.sum(UsageRecord.input_tokens).label("total_input_tokens"),
            func.sum(UsageRecord.output_tokens).label("total_output_tokens"),
            func.sum(UsageRecord.total_tokens).label("total_tokens"),
            func.count(UsageRecord.id).label("request_count")
        ).filter(
            UsageRecord.user_id == user_id,
            func.concat(
                func.extract("year", UsageRecord.created_at),
                "-",
                func.extract("month", UsageRecord.created_at)
            ) == year_month
        ).first()

        return {
            "year_month": year_month,
            "total_input_tokens": stats.total_input_tokens or 0,
            "total_output_tokens": stats.total_output_tokens or 0,
            "total_tokens": stats.total_tokens or 0,
            "request_count": stats.request_count or 0
        }

    def set_user_quota(self, user_id: int, monthly_quota: int) -> User:
        """Set monthly token quota for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.monthly_token_quota = monthly_quota
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_user_quota_info(self, user_id: int) -> dict:
        """Get complete quota information for a user."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        year_month = self.get_current_year_month()
        quota_record = self.get_or_create_quota_record(user_id, year_month)

        return {
            "user_id": user.id,
            "username": user.username,
            "monthly_token_quota": user.monthly_token_quota,
            "current_month_usage": quota_record.total_tokens,
            "current_year_month": year_month
        }
