"""
Wrap / unwrap interface for DEK.
Mock implementation: reverse bytes + base64. Production must use KMS/Transit.
"""
import base64
from typing import Tuple


def wrap_dek(dek: bytes) -> Tuple[str, str]:
    """
    Wrap base DEK for storage. Returns (wrapped_b64, key_version).
    Caller must store and pass same key_version on unwrap.
    """
    wrapped = base64.b64encode(dek[::-1]).decode("ascii")
    return wrapped, "kek:v1"


def unwrap_dek(wrapped_b64: str, key_version: str) -> bytes:
    """
    Unwrap to recover base DEK. key_version is not used in mock but required for API.
    """
    raw = base64.b64decode(wrapped_b64)
    return raw[::-1]
