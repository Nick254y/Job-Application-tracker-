import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def send_webhook_event(event_type: str, data: dict):
    """Send a webhook notification when a payment is received."""
    if not settings.webhook_url:
        logger.info("No webhook configured, skipping: %s", event_type)
        return

    try:
        httpx.post(
            settings.webhook_url,
            json={"event": event_type, "data": data},
            timeout=10,
        )
        logger.info("Webhook sent: %s", event_type)
    except Exception as e:
        logger.error("Webhook failed: %s", e)
