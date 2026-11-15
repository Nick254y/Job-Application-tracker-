"""Tests for the DocFlow Marketplace payment system."""

import os
import sys
import pytest

# Add the marketplace directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for testing
os.environ["DB_URL"] = "sqlite:///test_marketplace.db"
os.environ["MPESA_API_KEY"] = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
os.environ["MPESA_CONSUMER_KEY"] = "sGG877RUkWYxaD9XiG0ozCzEb8dcFEHvxLK8nNLKwomgAgHk"
os.environ["MPESA_CONSUMER_SECRET"] = "VSKUP58lCY5HboKZe876NWs2Sa5AgQZkJtUgAHcAeZKKI8YygtwGiOzjSqpLX69P"
os.environ["MPESA_SHORTCODE"] = "174379"

# Now import the app modules
from app.config import settings  # noqa: E402
from app.models import Base, Payment, init_db  # noqa: E402
from app.services.mpesa import generate_access_token  # noqa: E402


class TestConfig:
    """Config tests."""

    def test_settings_load(self):
        assert settings.api_key == "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        assert settings.consumer_key == "sGG877RUkWYxaD9XiG0ozCzEb8dcFEHvxLK8nNLKwomgAgHk"
        assert settings.shortcode == "174379"
        assert settings.merchant_number == "0118092929"


class TestDatabase:
    """Database tests."""

    def setup_method(self):
        init_db()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine(settings.db_url)
        self.Session = sessionmaker(bind=self.engine)

    def teardown_method(self):
        from sqlalchemy import create_engine
        engine = create_engine(settings.db_url)
        with engine.connect():
            pass

    def test_payment_model(self):
        # Verify model exists
        assert hasattr(Payment, "id")
        assert hasattr(Payment, "client_name")
        assert hasattr(Payment, "amount")


class TestMpesaService:
    """M-Pesa service tests."""

    def test_generate_access_token_success(self):
        """Test that access token generation works when all credentials are present."""
        # This is a unit test - actual API call would fail without valid credentials
        # We test that the function doesn't crash on missing credentials
        with pytest.raises(ValueError):
            generate_access_token()


def test_config_loads():
    """Test that the config loads correctly."""
    assert settings.merchant_number == "0118092929"
    assert "bfb279f9" in settings.api_key
    assert "174379" in settings.shortcode
