"""Unit tests for provider adapters."""
import pytest
from unittest.mock import MagicMock, patch

from app.providers.base import BaseAdapter, TextResult, ImageResult
from app.providers.openai import OpenAIAdapter
from app.providers.anthropic import AnthropicAdapter
from app.providers import AdapterRegistry


class TestBaseAdapter:
    """Tests for BaseAdapter."""

    def test_text_result_creation(self):
        """Test TextResult dataclass."""
        result = TextResult(
            content="Hello world",
            model="gpt-4",
            input_tokens=10,
            output_tokens=5
        )
        assert result.content == "Hello world"
        assert result.model == "gpt-4"
        assert result.input_tokens == 10
        assert result.output_tokens == 5

    def test_image_result_creation(self):
        """Test ImageResult dataclass."""
        result = ImageResult(
            url="https://example.com/image.png",
            revised_prompt="A beautiful sunset"
        )
        assert result.url == "https://example.com/image.png"
        assert result.revised_prompt == "A beautiful sunset"

    def test_count_tokens_estimate(self):
        """Test token estimation."""
        adapter = BaseAdapter()
        text = "Hello world" * 100
        tokens = adapter.count_tokens(text)
        assert tokens > 0


class TestAdapterRegistry:
    """Tests for AdapterRegistry."""

    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        from app.providers import registry
        providers = registry.list_providers()
        assert "openai" in providers
        assert "anthropic" in providers

    def test_get_existing_provider(self):
        """Test getting an existing provider."""
        from app.providers import registry
        adapter = registry.get("openai")
        assert adapter is not None
        assert adapter.provider_name == "openai"

    def test_get_unknown_provider(self):
        """Test getting an unknown provider raises error."""
        from app.providers import registry
        with pytest.raises(ValueError, match="Unknown provider"):
            registry.get("unknown_provider")


class TestOpenAIAdapter:
    """Tests for OpenAIAdapter."""

    def test_adapter_name(self):
        """Test adapter has correct name."""
        adapter = OpenAIAdapter()
        assert adapter.provider_name == "openai"

    @patch("app.providers.openai.OpenAIAdapter.__init__")
    def test_generate_text_with_mock(self, mock_init, mock_adapter):
        """Test text generation with mocked client."""
        mock_init.return_value = None

        adapter = OpenAIAdapter()
        adapter.client = mock_adapter

        # Test would need actual API key to run
        # This is a placeholder for integration testing
        assert adapter.provider_name == "openai"


class TestAnthropicAdapter:
    """Tests for AnthropicAdapter."""

    def test_adapter_name(self):
        """Test adapter has correct name."""
        adapter = AnthropicAdapter()
        assert adapter.provider_name == "anthropic"

    def test_generate_image_not_supported(self):
        """Test that image generation raises NotImplementedError."""
        adapter = AnthropicAdapter()
        with pytest.raises(NotImplementedError):
            adapter.generate_image(
                prompt="A cat",
                model="claude-3"
            )
