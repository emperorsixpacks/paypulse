import hashlib
import hmac


def sign_webhook(payload: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = sign_webhook(payload, secret)
    return hmac.compare_digest(expected, signature)
