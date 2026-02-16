"""Bundle validation: missing id, invalid base64."""
import pytest
from private_layer.crypto.models import Bundle
from private_layer.crypto.errors import BundleValidationError, DecryptError
from private_layer.pipeline.decrypt import decrypt_placeholders


def test_bundle_missing_id_raises():
    with pytest.raises(BundleValidationError):
        Bundle.from_dict({
            "nonce_b64": "aaa",
            "cipher_b64": "bbb",
            "aad": "aad",
            "wrapped_dek": "wd",
            "key_version": "kv",
        })
    with pytest.raises(BundleValidationError):
        Bundle.from_dict({"id": "", "nonce_b64": "a", "cipher_b64": "b", "aad": "a", "wrapped_dek": "w", "key_version": "k"})


def test_bundle_accepts_n_c_aliases():
    b = Bundle.from_dict({
        "id": "tid",
        "n": "YWFhYWFhYWFhYWFh",
        "c": "Yg==",
        "aad": "tenant=t|field=f|id=tid|schema=v1|req=r",
        "wd": "d2R3ZA==",
        "kv": "kek:v1",
    })
    assert b.nonce_b64 == "YWFhYWFhYWFhYWFh"
    assert b.cipher_b64 == "Yg=="


def test_decrypt_missing_bundle_id_raises():
    from private_layer.crypto.models import Bundle
    # Placeholder in text but no bundle for that id
    with pytest.raises(DecryptError):
        decrypt_placeholders(
            "Hello [EMAIL_unknown123]",
            [Bundle(id="other", nonce_b64="a", cipher_b64="b", aad="a", wrapped_dek="w", key_version="k")],
        )
