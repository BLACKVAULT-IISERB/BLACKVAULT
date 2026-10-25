import os
import base64

def signing_key_from_env() -> bytes:
    raw = os.environ.get("BLACKVAULT_HMAC_KEY", "")
    try:
        key = base64.b64decode(raw, validate=True)
    except (ValueError, TypeError):
        key = b""
    if len(key) < 32:
        raise ValueError("BLACKVAULT_HMAC_KEY must be base64 for at least 32 random bytes")
    return key
