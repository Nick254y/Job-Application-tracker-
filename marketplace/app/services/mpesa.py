import requests
import hmac
import hashlib
import base64
import time
from app.config import settings

MERCHANT_NUMBER = settings.merchant_number


def generate_access_token():
    """Generate M-Pesa Daraja access token using consumer_key and consumer_secret."""
    if not settings.consumer_key or not settings.consumer_secret:
        raise ValueError("Missing M-Pesa credentials (consumer_key, consumer_secret)")

    credentials = f"{settings.consumer_key}:{settings.consumer_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}
    response = requests.post(
        "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def simulate_stk_push(access_token, amount, phone, party_a, party_b, bill_ref, shortcode):
    """
    Send an M-Pesa STK Push (Mobile Money payment request) to the customer.

    This sends a payment request to the customer's phone. They approve it
    on their phone, and M-Pesa sends a callback to your webhook URL.

    Args:
        access_token: M-Pesa OAuth access token
        amount: Payment amount in KES
        phone: Customer's phone number (e.g., "0712345678")
        party_a: The customer's phone number (who is paying)
        party_b: Your business number (where money goes)
        bill_ref: Reference ID for the transaction
        shortcode: Your Safaricom shortcode (e.g., "600000")

    Returns:
        Dict with API response (ResponseCode, checkout_request_id, etc.)
    """
    if not settings.api_key:
        raise ValueError("Missing M-Pesa passkey (MPESA_API_KEY)")

    # For STK Push, the password is: passkey + timestamp (both uppercase)
    # The passkey is your MPESA_API_KEY
    timestamp = str(int(time.time()))
    password = base64.b64encode(f"{settings.api_key}{timestamp}".encode()).decode()

    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    data = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": party_a,  # Customer's phone
        "PartyB": party_b,  # Your recipient name
        "PhoneNumber": phone,
        "CallBackURL": f"{settings.webhook_url}/mpesa/callback",
        "AccountReference": "DocFlow Property Management",
        "TransactionDesc": f"Property payment from {phone}",
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers, timeout=30)
    return response.json()


def simulate_mpesa_request(amount, customer_phone, customer_name):
    """
    Complete M-Pesa payment request.
    Returns the API response with checkout_request_id.
    """
    token = generate_access_token()
    return simulate_stk_push(
        token,
        amount,
        customer_phone,
        MERCHANT_NUMBER,
        customer_name,
        f"DOCFLOW-{int(time.time())}",
        settings.shortcode,
    )
