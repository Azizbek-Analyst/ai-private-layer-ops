"""
DEK derivation with optional salt.
If salt provided: derived = HMAC(salt_bytes, base_dek, SHA256).
Else: return base_dek unchanged.
"""
from hashlib import sha256
from typing import Optional

import hmac as hmaclib


def derive_dek_with_salt(base_dek: bytes, salt: Optional[str] = None) -> bytes:
    """
    Derive DEK from base DEK and optional salt.
    - No salt: return base_dek.
    - With salt: HMAC-SHA256(salt_utf8, base_dek) as derived key.
    """
    if not salt:
        return base_dek
    salt_bytes = salt.encode("utf-8")
    return hmaclib.new(salt_bytes, base_dek, sha256).digest()
