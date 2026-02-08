"""
Configuration package for AI chatbot
Exports all configuration settings
"""
from .openrouter import openrouter_config, get_openrouter_config, validate_config, OpenRouterConfig

__all__ = ["openrouter_config", "get_openrouter_config", "validate_config", "OpenRouterConfig"]
