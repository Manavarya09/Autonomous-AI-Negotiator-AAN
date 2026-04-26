"""Autonomous AI Negotiator (AAN) - Core Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://aan:aanpass@localhost:5432/aan_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Email ( SMTP )
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    # IMAP
    imap_host: str = "imap.gmail.com"
    imap_user: str = ""
    imap_password: str = ""
    
    # Proxy (BrightData)
    brightdata_username: str = ""
    brightdata_password: str = ""
    
    # Exchange Rate API
    exchangerate_api_key: str = ""
    
    # App Settings
    app_name: str = "Autonomous AI Negotiator"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"


@lru_cache
def get_settings() -> Settings:
    return Settings()