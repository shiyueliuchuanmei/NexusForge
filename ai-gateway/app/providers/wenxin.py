"""Wenxin (Baidu) adapter."""
from typing import Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.providers.base import BaseAdapter, TextResult, ImageResult

settings = get_settings()


class WenxinAdapter(BaseAdapter):
    """Adapter for Baidu Wenxin API."""

    provider_name = "wenxin"

    def __init__(self):
        self.api_key = settings.wenxin_api_key
        self.secret_key = settings.wenxin_secret_key
        self._access_token = None

    def _get_access_token(self) -> str:
        """Get access token using API key and secret key."""
        auth_url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(auth_url, params=params)
            response.raise_for_status()
            return response.json()["access_token"]

    @property
    def access_token(self) -> str:
        """Lazy-load access token."""
        if self._access_token is None:
            self._access_token = self._get_access_token()
        return self._access_token

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """Generate text using Wenxin API."""
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}"

        # Convert messages to Wenxin format
        wenxin_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            wenxin_messages.append({"role": role, "content": msg["content"]})

        data = {
            "messages": wenxin_messages,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
        }

        if kwargs.get("max_tokens"):
            data["max_tokens"] = kwargs["max_tokens"]

        headers = {"Content-Type": "application/json"}
        params = {"access_token": self.access_token}

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=data,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            result = response.json()

        return TextResult(
            content=result["result"],
            model=model,
            input_tokens=result.get("usage", {}).get("prompt_tokens", 0),
            output_tokens=result.get("usage", {}).get("completion_tokens", 0),
            raw_response=result,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """Generate images using Wenxin API."""
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/image/{model}"

        data = {
            "prompt": prompt,
            "size": kwargs.get("size", "1024x1024"),
        }

        if kwargs.get("n"):
            data["n"] = kwargs["n"]

        headers = {"Content-Type": "application/json"}
        params = {"access_token": self.access_token}

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=data,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            result = response.json()

        results = []
        for item in result.get("data", []):
            results.append(ImageResult(
                url=item.get("url"),
                b64_json=item.get("b64_json"),
            ))

        return results
