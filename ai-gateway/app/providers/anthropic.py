"""Anthropic adapter for Claude models."""
from typing import Dict, List
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.providers.base import BaseAdapter, TextResult, ImageResult

settings = get_settings()


class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic API (Claude-3, etc.)."""

    provider_name = "anthropic"

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """Generate text using Anthropic Messages API."""
        # Anthropic uses system prompt separately
        system_prompt = ""
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        response = self.client.messages.create(
            model=model,
            system=system_prompt or None,
            messages=anthropic_messages,  # type: ignore
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            top_p=kwargs.get("top_p", 1.0),
            stop_sequences=kwargs.get("stop"),
        )

        return TextResult(
            content=response.content[0].text,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason,
            raw_response={
                "id": response.id,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            },
        )

    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """Anthropic does not support image generation."""
        raise NotImplementedError("Anthropic does not support image generation API")
