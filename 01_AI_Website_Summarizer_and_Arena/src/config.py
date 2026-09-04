"""
Configuration and Environment Management Module.
Loads environment variables safely and provides system-wide defaults.
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for AI Engineering application."""

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # API Base URLs
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Default Models
    DEFAULT_OPENAI_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    DEFAULT_GROQ_MODEL: str = os.getenv("GROQ_DEFAULT_MODEL", "openai/gpt-oss-120b")
    DEFAULT_ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-5-sonnet-20241022")

    # Available Provider Models Catalogue
    AVAILABLE_MODELS: Dict[str, List[str]] = {
        "OpenAI": [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
        ],
        "Groq": [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
            "groq/compound-mini",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
        "Anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
    }

    # Web Scraping Configuration
    SCRAPER_TIMEOUT: int = 15
    SCRAPER_MAX_CHARS: int = 25000  # avoid overflowing context limits

    # Scraper Request Headers (mimicking a genuine browser)
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }

    @classmethod
    def get_active_providers(cls) -> List[str]:
        """Returns a list of providers that have valid API keys set."""
        active = []
        if cls.OPENAI_API_KEY and not cls.OPENAI_API_KEY.startswith("sk-proj-your_"):
            active.append("OpenAI")
        if cls.GROQ_API_KEY and not cls.GROQ_API_KEY.startswith("gsk_your_"):
            active.append("Groq")
        if cls.ANTHROPIC_API_KEY and not cls.ANTHROPIC_API_KEY.startswith("sk-ant-your_"):
            active.append("Anthropic")
        return active
