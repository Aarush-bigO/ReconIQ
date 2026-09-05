"""
ReconIQ Enterprise — Application Configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://reconiq:reconiq@localhost:5432/reconiq"

    # Audit
    audit_hmac_secret: str = "reconiq-audit-secret-2026"

    # Logging
    log_level: str = "INFO"

    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # App
    app_env: str = "development"
    secret_key: str = "dev-secret-key"
    cors_origins: str = "http://localhost:3000"

    # Reconciliation defaults
    auto_match_threshold: float = 0.95
    review_threshold: float = 0.70
    date_tolerance_days: int = 3
    amount_tolerance_minor: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


_settings_instance = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
