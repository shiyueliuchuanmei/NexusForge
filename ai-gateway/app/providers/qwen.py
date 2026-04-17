"""Tongyi Qwen (Alibaba Cloud) adapter."""
from typing import Dict, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.providers.base import BaseAdapter, TextResult, ImageResult

settings = get_settings()


class QwenAdapter(BaseAdapter):
    """Adapter for Alibaba Cloud Tongyi Qwen API."""

    provider_name = "qwen"

    def __init__(self):
        self.api_key = settings.qwen_api_key
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """Make HTTP request to Qwen API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """Generate text using Qwen API."""
        data = {
            "model": model,
            "input": {"messages": messages},
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "top_p": kwargs.get("top_p", 1.0),
            },
        }

        if kwargs.get("stop"):
            data["parameters"]["stop"] = kwargs.get("stop")

        response = self._make_request("/services/aigc/text-generation/generation", data)

        return TextResult(
            content=response["output"]["text"],
            model=model,
            input_tokens=response["usage"].get("input_tokens", 0),
            output_tokens=response["usage"].get("output_tokens", 0),
            raw_response=response,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """Generate images using Qwen API."""
        data = {
            "model": model,
            "input": {"prompt": prompt},
            "parameters": {
                "size": kwargs.get("size", "1024x1024"),
            },
        }

        response = self._make_request("/services/aigc/image-generation/generation", data)

        results = []
        for item in response["output"]["images"]:
            results.append(ImageResult(
                url=item.get("url"),
                b64_json=item.get("b64_json"),
            ))

        return results
