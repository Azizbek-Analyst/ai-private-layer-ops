"""
Decrypt pipeline: match placeholders by regex, look up bundle by id,
unwrap base DEK, re-derive with salt, AES-GCM decrypt with same AAD.
"""
import re
from typing import List, Optional

from private_layer.crypto import aead, dek, wrap
from private_layer.crypto.errors import BundleValidationError, DecryptError
from private_layer.crypto.models import Bundle

PLACEHOLDER_RE = re.compile(r"\[([A-Z]+)_([A-Za-z0-9_\-]+)\]")


def decrypt_placeholders(
    text_with_placeholders: str,
    bundles: List[Bundle],
    salt: Optional[str] = None,
) -> str:
    """
    Restore plaintext by replacing each [FIELD_token_id] with decrypted value.
    Fails if bundle id missing, AAD/ciphertext/nonce tampered, or wrong salt.
    """
    by_id: dict[str, Bundle] = {}
    for b in bundles:
        if not b.id:
            raise BundleValidationError("Bundle missing required field: id")
        by_id[b.id] = b

    def repl(m: re.Match) -> str:
        _field, tok_id = m.group(1), m.group(2)
        b = by_id.get(tok_id)
        if not b:
            raise DecryptError(f"Bundle not found for placeholder id={tok_id!r}")
        try:
            base_dek = wrap.unwrap_dek(b.wrapped_dek, b.key_version)
        except Exception as e:
            raise DecryptError(f"Unwrap DEK failed: {e}") from e
        used_salt = b.salt if b.salt is not None else salt
        derived_dek = dek.derive_dek_with_salt(base_dek, used_salt)
        try:
            plain = aead.decrypt(
                derived_dek,
                b.nonce_b64,
                b.cipher_b64,
                b.aad,
            )
        except Exception as e:
            raise DecryptError(f"Decrypt failed (AAD/cipher/nonce tampered or wrong key): {e}") from e
        return plain.decode("utf-8")

    return PLACEHOLDER_RE.sub(repl, text_with_placeholders)
