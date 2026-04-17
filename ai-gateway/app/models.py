"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User model for API access control."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=False)
    monthly_token_quota = Column(BigInteger, default=1000000)  # Default 1M tokens
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usage_records = relationship("UsageRecord", back_populates="user")
    quota_records = relationship("QuotaRecord", back_populates="user")


class UsageRecord(Base):
    """Token usage record for tracking AI API consumption."""

    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, azure, qwen, wenxin
    model = Column(String(100), nullable=False)
    input_tokens = Column(BigInteger, default=0)
    output_tokens = Column(BigInteger, default=0)
    total_tokens = Column(BigInteger, default=0)
    request_type = Column(String(50), nullable=False)  # chat, image
    request_params = Column(Text, nullable=True)  # JSON string of request parameters
    response_data = Column(Text, nullable=True)  # JSON string of response
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_records")

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_usage_user_created", "user_id", "created_at"),
        Index("idx_usage_provider_model", "provider", "model"),
        Index("idx_usage_created_at", "created_at"),
    )


class QuotaRecord(Base):
    """Monthly quota record for each user."""

    __tablename__ = "quota_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year_month = Column(String(7), nullable=False)  # Format: "2024-01"
    total_tokens = Column(BigInteger, default=0)
    quota_limit = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quota_records")

    # Indexes
    __table_args__ = (
        Index("idx_quota_user_month", "user_id", "year_month", unique=True),
    )
