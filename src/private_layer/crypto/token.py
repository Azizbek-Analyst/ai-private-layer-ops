"""
Token ID generation: HMAC-SHA256(TOKEN_KEY, value) truncated to 9 bytes,
then base64url encoded without padding.
"""
import base64
from hashlib import sha256

import hmac as hmaclib

TOKEN_ID_LENGTH_BYTES = 9


def token_id(value: bytes, token_key: bytes, length_bytes: int = TOKEN_ID_LENGTH_BYTES) -> str:
    """
    Deterministic token ID. Same (token_key, value) always yields same id.
    """
    mac = hmaclib.new(token_key, value, sha256).digest()
    raw = mac[:length_bytes]
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")
