"""Ciphertext or nonce tampering causes decrypt failure."""
import base64
import pytest
from private_layer.core.types import Span
from private_layer.pipeline.encrypt import encrypt_spans
from private_layer.pipeline.decrypt import decrypt_placeholders
from private_layer.crypto.errors import DecryptError

TOKEN_KEY = b"2" * 32


def test_ciphertext_tampering_detected():
    text = "secret@test.com"
    spans = [Span(0, 15, "email", None, "regex")]
    masked, bundles = encrypt_spans(
        text, spans, token_key=TOKEN_KEY, tenant_id="t", schema="v1"
    )
    from private_layer.crypto.models import Bundle
    b = bundles[0]
    # Flip one byte in ciphertext (after b64 decode, modify, re-encode)
    raw = base64.b64decode(b.cipher_b64)
    tampered = bytes([raw[0] ^ 0xFF] + list(raw[1:]))
    bad_bundle = Bundle(
        id=b.id, nonce_b64=b.nonce_b64,
        cipher_b64=base64.b64encode(tampered).decode("ascii"),
        aad=b.aad, wrapped_dek=b.wrapped_dek, key_version=b.key_version, salt=b.salt,
    )
    with pytest.raises(DecryptError):
        decrypt_placeholders(masked, [bad_bundle])
