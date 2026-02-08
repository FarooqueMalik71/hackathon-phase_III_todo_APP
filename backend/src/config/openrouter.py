"""
OpenRouter API configuration for AI chatbot
Provides settings and configuration for OpenRouter integration
"""
import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class OpenRouterConfig(BaseModel):
    """OpenRouter configuration settings"""

    base_url: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("MODEL", "openai/gpt-3.5-turbo")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    timeout: int = int(os.getenv("AI_TIMEOUT", "30"))

    class Config:
        frozen = True  # Make config immutable


# Global configuration instance
openrouter_config = OpenRouterConfig()


def get_openrouter_config() -> OpenRouterConfig:
    """Get OpenRouter configuration"""
    return openrouter_config


def validate_config() -> bool:
    """Validate OpenRouter configuration"""
    if not openrouter_config.api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    if not openrouter_config.base_url:
        raise ValueError("OPENAI_BASE_URL environment variable is required")
    if not openrouter_config.model:
        raise ValueError("MODEL environment variable is required")
    return True
