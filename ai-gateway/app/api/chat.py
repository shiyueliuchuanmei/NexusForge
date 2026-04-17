"""Chat completion API routes."""
import json
import time
import uuid
from typing import Dict, List
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import ChatCompletionRequest, ChatCompletionResponse, Choice, Message, Usage
from app.providers import get_adapter
from app.services.quota import QuotaService

router = APIRouter(prefix="/v1", tags=["chat"])


def get_user_by_api_key(db: Session, api_key: str) -> User:
    """Validate API key and return user."""
    user = db.query(User).filter(User.api_key == api_key, User.is_active == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    provider: str = Header(None, description="AI provider: openai, anthropic, azure, qwen, wenxin"),
    x_api_key: str = Header(None, description="User API key for authentication"),
    db: Session = Depends(get_db)
):
    """
    Unified chat completions endpoint.
    Routes to the appropriate AI provider based on the provider header or model name.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = get_user_by_api_key(db, x_api_key)

    # Determine provider
    actual_provider = provider
    if not actual_provider:
        # Auto-detect provider from model name
        model_lower = request.model.lower()
        if "gpt" in model_lower or "dall" in model_lower:
            actual_provider = "openai"
        elif "claude" in model_lower:
            actual_provider = "anthropic"
        elif "qwen" in model_lower or "通义" in model_lower:
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

    # Prepare messages
    messages: List[Dict[str, str]] = [msg.model_dump() for msg in request.messages]

    # Check quota (estimate tokens)
    estimated_tokens = sum(len(m["content"]) // 4 for m in messages) + request.max_tokens
    quota_service = QuotaService(db)
    if not quota_service.check_quota(user.id, estimated_tokens):
        raise HTTPException(status_code=429, detail="Monthly token quota exceeded")

    # Generate text
    try:
        result = adapter.generate_text(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
            stop=request.stop
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider API error: {str(e)}")

    # Record usage
    quota_service.record_usage(
        user_id=user.id,
        provider=actual_provider,
        model=request.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        request_type="chat",
        request_params=json.dumps(request.model_dump(), ensure_ascii=False),
        response_data=json.dumps(result.raw_response, ensure_ascii=False) if result.raw_response else None
    )

    # Build response
    return ChatCompletionResponse(
        id=f"chat-{uuid.uuid4().hex[:12]}",
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=result.content),
                finish_reason=result.finish_reason
            )
        ],
        usage=Usage(
            prompt_tokens=result.input_tokens,
            completion_tokens=result.output_tokens,
            total_tokens=result.input_tokens + result.output_tokens
        )
    )
