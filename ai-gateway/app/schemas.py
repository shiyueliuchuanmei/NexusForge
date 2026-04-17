"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ Chat Completion Schemas ============

class Message(BaseModel):
    """Chat message schema."""
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """Request schema for /v1/chat/completions."""
    model: str = Field(description="Model identifier, e.g., gpt-4, claude-3-opus")
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None


class Choice(BaseModel):
    """Chat completion choice."""
    index: int
    message: Message
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Response schema for /v1/chat/completions."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


# ============ Image Generation Schemas ============

class ImageGenerationRequest(BaseModel):
    """Request schema for /v1/images/generations."""
    model: str = Field(description="Image model identifier, e.g., dall-e-3, stable-diffusion")
    prompt: str
    n: Optional[int] = 1
    size: Optional[str] = "1024x1024"
    response_format: Optional[str] = "url"


class ImageResult(BaseModel):
    """Single image result."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None


class ImageGenerationResponse(BaseModel):
    """Response schema for /v1/images/generations."""
    created: int
    data: List[ImageResult]


# ============ Admin Schemas ============

class AdminQuotaSetRequest(BaseModel):
    """Request schema for setting user quota."""
    user_id: int
    monthly_token_quota: int


class UsageStats(BaseModel):
    """Usage statistics for a user."""
    year_month: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    request_count: int


class UserQuotaInfo(BaseModel):
    """User quota information."""
    user_id: int
    username: str
    monthly_token_quota: int
    current_month_usage: int
    current_year_month: str


class AdminUsageQuery(BaseModel):
    """Query parameters for usage statistics."""
    user_id: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    year_month: Optional[str] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0
