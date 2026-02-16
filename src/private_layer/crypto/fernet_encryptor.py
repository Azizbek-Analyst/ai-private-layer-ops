"""
Optional Fernet encryptor — demo-level only.
Not part of core OSS; use for local/testing only. Production: use KMS/HSM.
"""
from typing import Optional

from .interface import Encryptor


class FernetEncryptor(Encryptor):
    """Fernet symmetric encryption. Requires: cryptography."""

    def __init__(self, key: bytes) -> None:
        try:
            from cryptography.fernet import Fernet
            from base64 import urlsafe_b64encode
        except ImportError:
            raise ImportError("Install cryptography for FernetEncryptor: pip install cryptography")
        # Fernet key = base64url(32 bytes)
        key_32 = key.ljust(32, b"\0")[:32] if len(key) < 32 else key[:32]
        self._f = Fernet(urlsafe_b64encode(key_32))

    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> bytes:
        return self._f.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes, aad: Optional[bytes] = None) -> bytes:
        return self._f.decrypt(ciphertext)
