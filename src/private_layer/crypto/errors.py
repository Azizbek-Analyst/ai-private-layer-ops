"""Crypto-specific exceptions."""

from private_layer.exceptions import PrivateLayerError


class CryptoError(PrivateLayerError):
    """Base for crypto operations."""


class DecryptError(CryptoError):
    """Decryption failed (tampering, wrong key, or invalid bundle)."""


class BundleValidationError(CryptoError):
    """Bundle missing required field or invalid encoding."""
