"""AAD tampering causes decrypt failure."""
import pytest
from private_layer.core.types import Span
from private_layer.pipeline.encrypt import encrypt_spans
from private_layer.pipeline.decrypt import decrypt_placeholders
from private_layer.crypto.errors import DecryptError

TOKEN_KEY = b"1" * 32


def test_aad_tampering_detected():
    text = "a@b.co"
    spans = [Span(0, 6, "email", None, "regex")]
    masked, bundles = encrypt_spans(
        text, spans, token_key=TOKEN_KEY, tenant_id="tenant1", schema="v1"
    )
    # Tamper AAD
    bundles[0] = type(bundles[0])(
        id=bundles[0].id,
        nonce_b64=bundles[0].nonce_b64,
        cipher_b64=bundles[0].cipher_b64,
        aad="tenant=other|field=email|id=" + bundles[0].id + "|schema=v1|req=req_ffff",
        wrapped_dek=bundles[0].wrapped_dek,
        key_version=bundles[0].key_version,
        salt=bundles[0].salt,
    )
    with pytest.raises(DecryptError):
        decrypt_placeholders(masked, bundles)
