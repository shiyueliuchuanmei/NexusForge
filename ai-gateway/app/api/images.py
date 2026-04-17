"""Image generation API routes."""
import json
import time
from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import ImageGenerationRequest, ImageGenerationResponse, ImageResult
from app.providers import get_adapter
from app.services.quota import QuotaService

router = APIRouter(prefix="/v1", tags=["images"])


def get_user_by_api_key(db: Session, api_key: str) -> User:
    """Validate API key and return user."""
    user = db.query(User).filter(User.api_key == api_key, User.is_active == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@router.post("/images/generations", response_model=ImageGenerationResponse)
async def image_generations(
    request: ImageGenerationRequest,
    provider: str = Header(None, description="AI provider: openai, azure, qwen, wenxin"),
    x_api_key: str = Header(None, description="User API key for authentication"),
    db: Session = Depends(get_db)
):
    """
    Unified image generation endpoint.
    Routes to the appropriate AI provider based on the provider header.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = get_user_by_api_key(db, x_api_key)

    # Determine provider
    actual_provider = provider
    if not actual_provider:
        model_lower = request.model.lower()
        if "dall" in model_lower:
            actual_provider = "openai"
        elif "stable" in model_lower:
            actual_provider = "openai"  # Could be Stability AI
        elif "通义" in model_lower or "qwen" in model_lower:
            actual_provider = "qwen"
        elif "文心" in model_lower or "ernie" in model_lower:
            actual_provider = "wenxin"
        else:
            actual_provider = "openai"  # Default

    # Get adapter
    try:
        adapter = get_adapter(actual_provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check quota (image generation is token-intensive)
    estimated_tokens = len(request.prompt) // 4 * 100  # Rough estimate
    quota_service = QuotaService(db)
    if not quota_service.check_quota(user.id, estimated_tokens):
        raise HTTPException(status_code=429, detail="Monthly token quota exceeded")

    # Generate images
    try:
        results = adapter.generate_image(
            prompt=request.prompt,
            model=request.model,
            n=request.n,
            size=request.size,
            response_format=request.response_format
        )
    except NotImplementedError:
        raise HTTPException(status_code=400, detail=f"Provider {actual_provider} does not support image generation")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider API error: {str(e)}")

    # Record usage (simplified for images)
    quota_service.record_usage(
        user_id=user.id,
        provider=actual_provider,
        model=request.model,
        input_tokens=estimated_tokens,
        output_tokens=0,
        request_type="image",
        request_params=json.dumps(request.model_dump(), ensure_ascii=False),
        response_data=None
    )

    # Build response
    image_results = [
        ImageResult(
            url=r.url,
            b64_json=r.b64_json,
            revised_prompt=r.revised_prompt
        )
        for r in results
    ]

    return ImageGenerationResponse(
        created=int(time.time()),
        data=image_results
    )
