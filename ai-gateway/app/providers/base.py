"""Base adapter class for AI providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TextResult:
    """Result container for text generation."""
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class ImageResult:
    """Result container for image generation."""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    revised_prompt: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseAdapter(ABC):
    """Abstract base class for AI provider adapters."""

    provider_name: str = "base"

    @abstractmethod
    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> TextResult:
        """
        Generate text from the AI model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            TextResult with generated content and token usage
        """
        pass

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        model: str,
        **kwargs
    ) -> List[ImageResult]:
        """
        Generate images from the AI model.

        Args:
            prompt: Image description
            model: Model identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            List of ImageResult
        """
        pass

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text (approximate)."""
        # Rough estimate: ~4 characters per token for English
        return len(text) // 4
