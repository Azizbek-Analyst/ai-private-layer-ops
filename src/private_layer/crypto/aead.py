"""
AES-256-GCM encrypt/decrypt helpers.
- 12-byte random nonce per fragment
- AAD bound to plaintext; tampering causes decrypt failure
"""
import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_LENGTH = 12
KEY_BITS = 256


def generate_dek() -> bytes:
    """Generate a new 256-bit DEK for AES-GCM."""
    return AESGCM.generate_key(bit_length=KEY_BITS)


def encrypt(dek: bytes, plaintext: bytes, aad: str) -> Tuple[str, str]:
    """
    Encrypt plaintext with DEK and AAD. Returns (nonce_b64, cipher_b64).
    Nonce is 12 bytes, random.
    """
    nonce = os.urandom(NONCE_LENGTH)
    aes = AESGCM(dek)
    ciphertext = aes.encrypt(nonce, plaintext, aad.encode("utf-8"))
    return base64.b64encode(nonce).decode("ascii"), base64.b64encode(ciphertext).decode("ascii")


def decrypt(dek: bytes, nonce_b64: str, cipher_b64: str, aad: str) -> bytes:
    """
    Decrypt with DEK and same AAD. Raises on tampering or wrong key.
    """
    try:
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(cipher_b64)
    except Exception as e:
        raise ValueError(f"Invalid base64 in bundle: {e}") from e
    if len(nonce) != NONCE_LENGTH:
        raise ValueError(f"Nonce must be {NONCE_LENGTH} bytes, got {len(nonce)}")
    aes = AESGCM(dek)
    return aes.decrypt(nonce, ciphertext, aad.encode("utf-8"))
