from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    claude_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Database
    db_url: str = "sqlite:///job_tracker.db"

    # Queue/Scheduler
    queue_type: str = "cron"  # cron, celery, or hosted

    # Alerts
    alerts_email: str = ""
    alerts_webhook_url: str = ""

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
