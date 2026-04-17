"""Application configuration."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ai_gateway"

    # OpenAI
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"

    # Anthropic
    anthropic_api_key: str = ""

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"

    # Tongyi Qwen
    qwen_api_key: str = ""

    # Wenxin
    wenxin_api_key: str = ""
    wenxin_secret_key: str = ""

    # Admin
    admin_api_key: str = "sk-admin-default"

    # Default provider
    default_provider: str = "openai"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
