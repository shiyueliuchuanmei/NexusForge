"""OpenAI adapter for GPT models."""
from typing import Dict, List, Any, Optional
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.providers.base import BaseAdapter, TextResult, ImageResult

settings = get_settings()


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI API (GPT-4, DALL-E, etc.)."""

    provider_name = "openai"

    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """Generate text using OpenAI Chat Completion API."""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
            top_p=kwargs.get("top_p", 1.0),
            frequency_penalty=kwargs.get("frequency_penalty", 0.0),
            presence_penalty=kwargs.get("presence_penalty", 0.0),
            stop=kwargs.get("stop"),
            stream=False,
        )

        choice = response.choices[0]
        content = choice.message.content or ""

        return TextResult(
            content=content,
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump(),
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """Generate images using OpenAI DALL-E API."""
        response = self.client.images.generate(
            model=model or "dall-e-3",
            prompt=prompt,
            n=kwargs.get("n", 1),
            size=kwargs.get("size", "1024x1024"),
            response_format=kwargs.get("response_format", "url"),
        )

        results = []
        for item in response.data:
            results.append(ImageResult(
                url=item.url,
                b64_json=item.b64_json,
                revised_prompt=item.revised_prompt,
                raw_response=item.model_dump(),
            ))

        return results
