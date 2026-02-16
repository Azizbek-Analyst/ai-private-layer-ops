"""
Encrypt pipeline: generate DEK, wrap it, derive with salt, encrypt each span,
replace with placeholder [FIELD_token_id]. Replace from end to start.
"""
import os
from typing import List, Optional

from private_layer.core.types import Span
from private_layer.crypto import aad, aead, dek, token, wrap
from private_layer.crypto.models import Bundle
from private_layer.crypto.aead import generate_dek


def encrypt_spans(
    text: str,
    spans: List[Span],
    token_key: bytes,
    tenant_id: str,
    schema: str = "v1",
    request_id: Optional[str] = None,
    salt: Optional[str] = None,
) -> tuple[str, List[Bundle]]:
    """
    Encrypt each span with AES-256-GCM, replace with [FIELD_token_id].
    Returns (text_with_placeholders, bundles). Bundles store wrapped base DEK and salt.
    """
    request_id = request_id or ("req_" + os.urandom(4).hex())
    base_dek = generate_dek()
    derived_dek = dek.derive_dek_with_salt(base_dek, salt)
    wrapped_dek_b64, key_version = wrap.wrap_dek(base_dek)

    # Sort by start descending for safe in-place replacement
    ordered = sorted(spans, key=lambda s: s.start, reverse=True)
    buf = text
    bundles: List[Bundle] = []

    for s in ordered:
        raw = buf[s.start : s.end]
        raw_bytes = raw.strip().encode("utf-8")
        tok_id = token.token_id(raw_bytes, token_key)
        aad_str = aad.build_aad(tenant_id, s.label, tok_id, schema, request_id)
        nonce_b64, cipher_b64 = aead.encrypt(derived_dek, raw.encode("utf-8"), aad_str)
        bundles.append(
            Bundle(
                id=tok_id,
                nonce_b64=nonce_b64,
                cipher_b64=cipher_b64,
                aad=aad_str,
                wrapped_dek=wrapped_dek_b64,
                key_version=key_version,
                salt=salt,
            )
        )
        placeholder = f"[{s.label.upper()}_{tok_id}]"
        buf = buf[: s.start] + placeholder + buf[s.end :]

    bundles.reverse()
    return buf, bundles
