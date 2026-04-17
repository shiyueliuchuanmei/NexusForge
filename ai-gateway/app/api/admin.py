"""Admin API routes for quota management."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UsageRecord
from app.schemas import AdminQuotaSetRequest, UserQuotaInfo, UsageStats
from app.services.quota import QuotaService
from app.config import get_settings

router = APIRouter(prefix="/admin", tags=["admin"])

settings = get_settings()


def verify_admin_api_key(x_admin_key: str = Header(None)) -> bool:
    """Verify admin API key."""
    if not x_admin_key:
        raise HTTPException(status_code=401, detail="Admin API key required")
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    return True


@router.post("/quota/set")
def set_user_quota(
    request: AdminQuotaSetRequest,
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """Set monthly token quota for a user."""
    quota_service = QuotaService(db)
    user = quota_service.set_user_quota(request.user_id, request.monthly_token_quota)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"Quota set to {request.monthly_token_quota} for user {user.username}"}


@router.get("/quota/{user_id}", response_model=UserQuotaInfo)
def get_user_quota(
    user_id: int,
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """Get quota information for a specific user."""
    quota_service = QuotaService(db)
    info = quota_service.get_user_quota_info(user_id)

    if not info:
        raise HTTPException(status_code=404, detail="User not found")

    return info


@router.get("/usage/stats/{user_id}", response_model=List[UsageStats])
def get_user_usage_stats(
    user_id: int,
    year_month: Optional[str] = Query(None, description="Format: YYYY-MM"),
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """Get usage statistics for a user."""
    quota_service = QuotaService(db)
    stats = quota_service.get_user_usage_stats(user_id, year_month)
    return [UsageStats(**stats)]


@router.get("/usage/records")
def get_usage_records(
    user_id: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    year_month: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """Query usage records with filters."""
    query = db.query(UsageRecord)

    if user_id:
        query = query.filter(UsageRecord.user_id == user_id)
    if provider:
        query = query.filter(UsageRecord.provider == provider)
    if model:
        query = query.filter(UsageRecord.model == model)

    records = query.order_by(UsageRecord.created_at.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "provider": r.provider,
            "model": r.model,
            "input_tokens": r.input_tokens,
            "output_tokens": r.output_tokens,
            "total_tokens": r.total_tokens,
            "request_type": r.request_type,
            "created_at": r.created_at.isoformat()
        }
        for r in records
    ]


@router.get("/users")
def list_users(
    _: bool = Depends(verify_admin_api_key),
    db: Session = Depends(get_db)
):
    """List all users."""
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "monthly_token_quota": u.monthly_token_quota,
            "is_active": u.is_active == 1,
            "created_at": u.created_at.isoformat()
        }
        for u in users
    ]
