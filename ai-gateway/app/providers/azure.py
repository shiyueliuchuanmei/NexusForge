"""Azure OpenAI adapter using httpx."""
from typing import Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.providers.base import BaseAdapter, TextResult, ImageResult

settings = get_settings()


class AzureOpenAIAdapter(BaseAdapter):
    """Adapter for Azure OpenAI Service using REST API."""

    provider_name = "azure"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """Generate text using Azure OpenAI Chat Completion API."""
        url = f"{settings.azure_openai_endpoint}/openai/deployments/{model}/chat/completions?api-version={settings.azure_openai_api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": settings.azure_openai_api_key,
        }

        payload = {
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
            "top_p": kwargs.get("top_p", 1.0),
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return TextResult(
            content=choice["message"]["content"],
            model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason"),
            raw_response=data,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """Generate images using Azure OpenAI DALL-E API."""
        url = f"{settings.azure_openai_endpoint}/openai/deployments/{model}/images/generations?api-version={settings.azure_openai_api_version}"

        headers = {
            "Content-Type": "application/json",
            "api-key": settings.azure_openai_api_key,
        }

        payload = {
            "prompt": prompt,
            "n": kwargs.get("n", 1),
            "size": kwargs.get("size", "1024x1024"),
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("data", []):
            results.append(ImageResult(
                url=item.get("url"),
                b64_json=item.get("b64_json"),
            ))

        return results
