"""Alert and notification system.

Sends alerts to email, webhook, and other notification channels
when important events occur (e.g., payment received, job match found).
"""

import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def send_alert(alert_type: str, message: str, recipient: str = None):
    """
    Send an alert for a significant event.

    Args:
        alert_type: Type of alert (e.g., "payment_received", "lead_found", "maintenance_request")
        message: The alert message content
        recipient: Email or webhook URL (optional, uses config if not provided)
    """
    if not recipient:
        recipient = settings.alerts_email or settings.alerts_webhook_url

    if not recipient:
        logger.warning("No alert recipient configured, skipping alert: %s", alert_type)
        return

    alert_data = {
        "timestamp": "2026-11-15T12:00:00Z",
        "alert_type": alert_type,
        "message": message,
        "status": "triggered",
    }

    try:
        if "@" in recipient and "@" not in recipient.split("//")[-1]:
            # Likely an email
            logger.info("Sending email alert to %s: %s", recipient, message)
            # In production, use an email service
        else:
            # Likely a webhook URL
            logger.info("Sending webhook alert to %s: %s", recipient, message)
            requests.post(
                recipient,
                json=alert_data,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
    except Exception as e:
        logger.error("Failed to send alert: %s", e)


def send_job_match_alert(job_title: str, company: str, match_score: int, user_id: str):
    """Send an alert for a new job match.

    This is a convenience function for the specific case of job matches.
    """
    email = settings.alerts_email
    if email:
        send_alert(
            "job_match",
            f"New match for user {user_id}: {job_title} at {company} (score: {match_score}/100)",
            recipient=email,
        )
