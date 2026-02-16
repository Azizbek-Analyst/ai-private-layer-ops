"""Optional encryptor interface (demo-level; not part of core OSS guarantee)."""
from abc import ABC, abstractmethod
from typing import Optional


class Encryptor(ABC):
    """Minimal interface for optional encryption of mapping values."""

    @abstractmethod
    def encrypt(self, plaintext: bytes, aad: Optional[bytes] = None) -> bytes:
        ...

    @abstractmethod
    def decrypt(self, ciphertext: bytes, aad: Optional[bytes] = None) -> bytes:
        ...
