"""
Gemini API Configuration for DSPy Optimization

Configures Google Gemini API (free tier) for DSPy training.
Provides LM backend for agent optimization.

Week 6 Day 2
Version: 8.0.0
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class GeminiModel(Enum):
    """Available Gemini models for DSPy."""
    FLASH = "gemini-1.5-flash"  # Fast, efficient (free tier)
    PRO = "gemini-1.5-pro"      # More capable (paid)


@dataclass
class GeminiConfig:
    """Configuration for Gemini API."""

    # API Configuration
    api_key: str = ""  # Set via GEMINI_API_KEY env variable
    model: GeminiModel = GeminiModel.FLASH

    # Generation Parameters
    temperature: float = 0.7
    max_output_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40

    # Rate Limiting (Free Tier)
    requests_per_minute: int = 15
    requests_per_day: int = 1500
    tokens_per_minute: int = 1_000_000

    # Safety Settings
    block_none: bool = True  # Don't block any content for development

    # Retry Configuration
    max_retries: int = 3
    retry_delay_sec: float = 2.0


class GeminiConfigManager:
    """Manages Gemini API configuration."""

    def __init__(self):
        self.config: Optional[GeminiConfig] = None

    def load_from_env(self) -> GeminiConfig:
        """
        Load configuration from environment variables.

        Environment variables:
        - GEMINI_API_KEY: Required API key
        - GEMINI_MODEL: Optional model selection (default: flash)
        - GEMINI_TEMPERATURE: Optional temperature (default: 0.7)

        Returns:
            GeminiConfig instance
        """
        api_key = os.getenv("GEMINI_API_KEY", "")

        if not api_key:
            print("WARNING: GEMINI_API_KEY not set. Using placeholder.")
            print("Set via: export GEMINI_API_KEY='your-api-key'")
            api_key = "PLACEHOLDER_KEY"

        model_name = os.getenv("GEMINI_MODEL", "flash")
        model = GeminiModel.FLASH if model_name == "flash" else GeminiModel.PRO

        temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))

        self.config = GeminiConfig(
            api_key=api_key,
            model=model,
            temperature=temperature
        )

        return self.config

    def validate_config(self) -> bool:
        """
        Validate configuration is ready for use.

        Returns:
            True if valid, False otherwise
        """
        if not self.config:
            print("ERROR: Configuration not loaded. Call load_from_env() first.")
            return False

        if self.config.api_key == "PLACEHOLDER_KEY":
            print("ERROR: GEMINI_API_KEY not configured.")
            print("Get your API key from: https://makersuite.google.com/app/apikey")
            return False

        if self.config.temperature < 0 or self.config.temperature > 2:
            print(f"ERROR: Invalid temperature {self.config.temperature}. Must be 0-2.")
            return False

        return True

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for logging."""
        if not self.config:
            return {"status": "not_loaded"}

        return {
            "model": self.config.model.value,
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_output_tokens,
            "api_key_set": self.config.api_key != "PLACEHOLDER_KEY",
            "free_tier_limits": {
                "requests_per_minute": self.config.requests_per_minute,
                "requests_per_day": self.config.requests_per_day,
                "tokens_per_minute": self.config.tokens_per_minute
            }
        }


def create_gemini_config() -> GeminiConfigManager:
    """Factory function to create Gemini config manager."""
    manager = GeminiConfigManager()
    manager.load_from_env()
    return manager


# Example usage and setup instructions
SETUP_INSTRUCTIONS = """
Gemini API Setup Instructions
==============================

1. Get API Key:
   - Visit: https://makersuite.google.com/app/apikey
   - Create new API key (free tier)
   - Copy the key

2. Set Environment Variable:

   Linux/Mac:
   export GEMINI_API_KEY='your-api-key-here'

   Windows (PowerShell):
   $env:GEMINI_API_KEY='your-api-key-here'

   Windows (CMD):
   set GEMINI_API_KEY=your-api-key-here

3. Optional Configuration:
   export GEMINI_MODEL='flash'  # or 'pro'
   export GEMINI_TEMPERATURE='0.7'

4. Verify Setup:
   python -c "from src.dspy_optimization.gemini_config import create_gemini_config; \
              mgr = create_gemini_config(); \
              print('Valid:', mgr.validate_config())"

5. Free Tier Limits:
   - 15 requests/minute
   - 1,500 requests/day
   - 1M tokens/minute

   Monitor usage at: https://makersuite.google.com/app/usage
"""


if __name__ == "__main__":
    # Print setup instructions
    print(SETUP_INSTRUCTIONS)

    # Test configuration
    print("\nTesting Configuration:")
    print("=" * 80)

    manager = create_gemini_config()
    summary = manager.get_config_summary()

    print(f"\nModel: {summary.get('model', 'N/A')}")
    print(f"Temperature: {summary.get('temperature', 'N/A')}")
    print(f"Max Tokens: {summary.get('max_output_tokens', 'N/A')}")
    print(f"API Key Set: {summary.get('api_key_set', False)}")

    print("\nFree Tier Limits:")
    limits = summary.get('free_tier_limits', {})
    print(f"  Requests/minute: {limits.get('requests_per_minute', 'N/A')}")
    print(f"  Requests/day: {limits.get('requests_per_day', 'N/A')}")
    print(f"  Tokens/minute: {limits.get('tokens_per_minute', 'N/A'):,}")

    print("\nValidation:", "PASS" if manager.validate_config() else "FAIL")
    print("=" * 80)
