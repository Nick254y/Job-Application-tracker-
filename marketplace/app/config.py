import os


class Settings:
    """Application settings loaded from environment variables."""

    # Database
    db_url: str = os.getenv("DB_URL", "sqlite:///marketplace.db")

    # Your mobile money number (Kenyan phone, no + or leading 0)
    merchant_number: str = os.getenv("MERCHANT_NUMBER", "0118092929")

    # M-Pesa Daraja API credentials
    # Note: Your API Key (passkey) is used for STK Push authentication
    api_key: str = os.getenv("MPESA_API_KEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
    consumer_key: str = os.getenv("MPESA_CONSUMER_KEY", "sGG877RUkWYxaD9XiG0ozCzEb8dcFEHvxLK8nNLKwomgAgHk")
    consumer_secret: str = os.getenv("MPESA_CONSUMER_SECRET", "VSKUP58lCY5HboKZe876NWs2Sa5AgQZkJtUgAHcAeZKKI8YygtwGiOzjSqpLX69P")
    shortcode: str = os.getenv("MPESA_SHORTCODE", "174379")

    # Email/SMTP
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("FROM_EMAIL", "no-reply@docflow.com")

    # Webhook
    webhook_url: str = os.getenv("WEBHOOK_URL", "")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
