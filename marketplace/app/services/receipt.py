import logging
from app.config import settings

logger = logging.getLogger(__name__)


def send_payment_receipt(client_email: str, client_name: str, property_name: str, amount: float, payment_id: int, status: str = "paid"):
    """Send a payment receipt to the client via email."""
    if not settings.smtp_user:
        logger.info("No SMTP configured, skipping receipt to %s", client_email)
        return

    try:
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["Subject"] = f"Payment Receipt {payment_id} - {property_name}"
        msg["From"] = settings.from_email
        msg["To"] = client_email

        msg.set_content(f"""
Dear {client_name},

Thank you for your payment of ₦{amount:,.2f} for {property_name}.

Payment Details:
- Receipt ID: #{payment_id}
- Amount: ₦{amount:,.2f}
- Method: {'N/A'}
- Status: {status}
- Date: {datetime.utcnow().strftime('%Y-%m-%d')}

This confirms your payment has been received.

Best regards,
DocFlow Property Management
        """)

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        logger.info("Receipt sent to %s for payment #%d", client_email, payment_id)

    except Exception as e:
        logger.error("Failed to send receipt: %s", e)
