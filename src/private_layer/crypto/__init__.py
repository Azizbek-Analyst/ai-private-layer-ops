"""
AES-256-GCM envelope encryption: token_id, AAD, DEK derivation, wrap/unwrap, Bundle.
"""
from private_layer.crypto.aad import build_aad
from private_layer.crypto.aead import decrypt as aead_decrypt
from private_layer.crypto.aead import encrypt as aead_encrypt
from private_layer.crypto.aead import generate_dek
from private_layer.crypto.dek import derive_dek_with_salt
from private_layer.crypto.models import Bundle
from private_layer.crypto.token import token_id
from private_layer.crypto.wrap import unwrap_dek, wrap_dek
from private_layer.crypto.errors import BundleValidationError, CryptoError, DecryptError

__all__ = [
    "token_id",
    "build_aad",
    "aead_encrypt",
    "aead_decrypt",
    "generate_dek",
    "derive_dek_with_salt",
    "wrap_dek",
    "unwrap_dek",
    "Bundle",
    "CryptoError",
    "DecryptError",
    "BundleValidationError",
]
