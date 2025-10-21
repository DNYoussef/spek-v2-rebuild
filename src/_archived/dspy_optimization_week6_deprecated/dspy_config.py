"""DSPy Configuration for Gemini CLI Integration (Week 6 Day 3, v8.0.1)

Configures DSPy to use Gemini CLI (v0.3.4) already installed on system.
Uses custom GeminiCLIAdapter as LM backend.
"""

import os
import dspy
from typing import Optional
from dataclasses import dataclass
from src.dspy_optimization.gemini_cli_adapter import GeminiCLIAdapter


@dataclass
class DSPyConfig:
    """Configuration for DSPy optimization with Gemini CLI."""

    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048

    def __post_init__(self):
        """Validate configuration."""
        assert 0.0 <= self.temperature <= 1.0, "Temperature must be 0.0-1.0"
        assert self.max_tokens > 0, "Max tokens must be positive"


def configure_dspy(
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> None:
    """Configure DSPy to use Gemini CLI as the language model backend.

    Uses GeminiCLIAdapter to wrap the existing Gemini CLI installation.
    No API key required (CLI handles authentication).

    Args:
        model: Gemini model name (default: gemini-1.5-flash)
        temperature: Sampling temperature 0.0-1.0 (default: 0.7)
        max_tokens: Maximum output tokens (default: 2048)

    Raises:
        RuntimeError: If Gemini CLI not available

    Example:
        >>> configure_dspy()  # Uses defaults
        >>> configure_dspy(temperature=0.5, max_tokens=1024)
    """
    config = DSPyConfig(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

    try:
        adapter = GeminiCLIAdapter(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )

        # Test with simple forward() call
        test_response = adapter.forward(prompt="Test connection: What is 2+2?")

        # Check if response is valid
        if not test_response or not test_response.choices:
            raise RuntimeError("Gemini CLI test failed: No response received")

        response_text = test_response.choices[0].message.content
        if not response_text:
            raise RuntimeError("Gemini CLI test failed: Empty response")

        dspy.settings.configure(lm=adapter)

        print(f"[OK] DSPy configured with Gemini CLI {config.model}")
        print(f"     Temperature: {config.temperature}")
        print(f"     Max tokens: {config.max_tokens}")
        print(f"     CLI version: v0.3.4")
        print(f"     Test response: {response_text[:100]}")  # First 100 chars

    except Exception as e:
        raise RuntimeError(f"Failed to configure DSPy with Gemini CLI: {e}")


def get_current_config() -> Optional[GeminiCLIAdapter]:
    """Get currently configured DSPy language model.

    Returns:
        Configured GeminiCLIAdapter or None if not configured

    Example:
        >>> lm = get_current_config()
        >>> if lm:
        ...     print(f"Using model: {lm.model}")
    """
    return dspy.settings.lm if hasattr(dspy.settings, 'lm') else None


def validate_api_connection() -> bool:
    """Validate Gemini CLI connection by making a test request.

    Returns:
        True if connection successful, False otherwise

    Example:
        >>> if validate_api_connection():
        ...     print("Gemini CLI ready")
    """
    try:
        lm = get_current_config()
        if not lm:
            print("[FAIL] DSPy not configured. Call configure_dspy() first.")
            return False

        if not isinstance(lm, GeminiCLIAdapter):
            print("[WARN] LM is not GeminiCLIAdapter, skipping validation")
            return True

        # Use forward() method (BaseLM interface)
        test_response = lm.forward(prompt="What is 2+2?")

        if test_response and test_response.choices:
            response_text = test_response.choices[0].message.content
            print("[OK] Gemini CLI connection validated")
            print(f"     Response: {response_text[:50]}")
            return True
        else:
            print(f"[FAIL] Gemini CLI returned invalid response")
            return False

    except Exception as e:
        print(f"[FAIL] Gemini CLI connection failed: {e}")
        return False


# Version: 1.1
# Timestamp: 2025-10-08T00:00:00-04:00
# Agent/Model: Claude Sonnet 4.5
# Changes: Updated to use Gemini CLI adapter instead of google-generativeai SDK
# Status: COMPLETE
#
# Receipt:
# run_id: week6-day3-dspy-config-cli
# inputs: [gemini_cli_adapter.py, DSPY-INTEGRATION-STRATEGY.md]
# tools_used: [Edit]
# changes: Replaced SDK integration with CLI adapter, removed API key requirement
