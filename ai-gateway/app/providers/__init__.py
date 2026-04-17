"""Provider adapter factory and registry."""
from typing import Dict
from app.providers.base import BaseAdapter, TextResult, ImageResult
from app.providers.openai import OpenAIAdapter
from app.providers.anthropic import AnthropicAdapter
from app.providers.azure import AzureOpenAIAdapter
from app.providers.qwen import QwenAdapter
from app.providers.wenxin import WenxinAdapter


class AdapterRegistry:
    """Registry for AI provider adapters."""

    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}

    def register(self, provider: str, adapter: BaseAdapter):
        """Register an adapter for a provider."""
        self._adapters[provider] = adapter

    def get(self, provider: str) -> BaseAdapter:
        """Get adapter for a provider."""
        if provider not in self._adapters:
            raise ValueError(f"Unknown provider: {provider}")
        return self._adapters[provider]

    def list_providers(self) -> list:
        """List all registered providers."""
        return list(self._adapters.keys())


# Global registry instance
registry = AdapterRegistry()

# Register default adapters
registry.register("openai", OpenAIAdapter())
registry.register("anthropic", AnthropicAdapter())
registry.register("azure", AzureOpenAIAdapter())
registry.register("qwen", QwenAdapter())
registry.register("wenxin", WenxinAdapter())


def get_adapter(provider: str) -> BaseAdapter:
    """Get adapter for a provider."""
    return registry.get(provider)
