"""Application configuration using pydantic-settings."""

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MOCK = "mock"


class LogFormat(str, Enum):
    """Log output formats."""
    
    JSON = "json"
    CONSOLE = "console"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "AI Campaign Analyst"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.MOCK
    llm_timeout: int = 30
    llm_temperature: float = 0.3
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Anthropic (Claude)
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Google (Gemini)
    google_api_key: Optional[str] = None
    google_model: str = "gemini-2.0-flash"
    
    # Logging
    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.CONSOLE
    
    # Validation thresholds
    outlier_threshold: float = 1.5  # IQR multiplier
    min_impressions_threshold: int = 1000
    high_ctr_threshold: float = 5.0  # %
    low_conversion_rate_threshold: float = 1.0  # %
    high_cpa_multiplier: float = 2.0  # x average
    
    def get_active_llm_key(self) -> Optional[str]:
        """Return the API key for the active LLM provider."""
        match self.llm_provider:
            case LLMProvider.OPENAI:
                return self.openai_api_key
            case LLMProvider.CLAUDE:
                return self.anthropic_api_key
            case LLMProvider.GEMINI:
                return self.google_api_key
            case _:
                return None
    
    def is_llm_configured(self) -> bool:
        """Check if an LLM provider is properly configured."""
        if self.llm_provider == LLMProvider.MOCK:
            return True
        return self.get_active_llm_key() is not None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
