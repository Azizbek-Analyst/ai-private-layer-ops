"""Roundtrip encrypt/decrypt with pipeline."""
import pytest
from private_layer.core.types import Span
from private_layer.pipeline.encrypt import encrypt_spans
from private_layer.pipeline.decrypt import decrypt_placeholders

TOKEN_KEY = b"0" * 32


def test_roundtrip_no_salt():
    text = "Email john@example.com and phone +1 555 123 4567."
    spans = [
        Span(6, 22, "email", None, "regex"),
        Span(32, 46, "phone", None, "regex"),
    ]
    masked, bundles = encrypt_spans(
        text,
        spans,
        token_key=TOKEN_KEY,
        tenant_id="test",
        schema="v1",
        salt=None,
    )
    assert masked != text
    assert len(bundles) == 2
    for b in bundles:
        assert b.salt is None
    restored = decrypt_placeholders(masked, bundles, salt=None)
    assert restored == text


def test_roundtrip_with_salt():
    text = "Secret: alice@test.com"
    spans = [Span(8, 22, "email", None, "regex")]
    masked, bundles = encrypt_spans(
        text,
        spans,
        token_key=TOKEN_KEY,
        tenant_id="t1",
        salt="my-salt",
    )
    assert len(bundles) == 1
    assert bundles[0].salt == "my-salt"
    restored = decrypt_placeholders(masked, bundles, salt=None)
    assert restored == text


def test_wrong_salt_fails():
    text = "x@y.com"
    spans = [Span(0, 6, "email", None, "regex")]
    masked, bundles = encrypt_spans(
        text, spans, token_key=TOKEN_KEY, tenant_id="t", salt="salt1"
    )
    from private_layer.crypto.errors import DecryptError
    from private_layer.crypto.models import Bundle
    # Clear bundle salt so decrypt uses request salt; pass wrong salt
    b = bundles[0]
    wrong_bundle = Bundle(
        id=b.id, nonce_b64=b.nonce_b64, cipher_b64=b.cipher_b64, aad=b.aad,
        wrapped_dek=b.wrapped_dek, key_version=b.key_version, salt=None,
    )
    with pytest.raises(DecryptError):
        decrypt_placeholders(masked, [wrong_bundle], salt="wrong-salt")
