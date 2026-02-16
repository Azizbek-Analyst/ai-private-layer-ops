"""Token ID determinism and length."""
from private_layer.crypto.token import token_id, TOKEN_ID_LENGTH_BYTES

KEY = b"k" * 32


def test_token_id_deterministic():
    v = b"john@example.com"
    a = token_id(v, KEY)
    b = token_id(v, KEY)
    assert a == b


def test_token_id_different_for_different_value():
    a = token_id(b"a@b.co", KEY)
    b = token_id(b"x@y.com", KEY)
    assert a != b


def test_token_id_different_for_different_key():
    v = b"same@value.com"
    a = token_id(v, KEY)
    b = token_id(v, b"x" * 32)
    assert a != b


def test_token_id_length():
    import base64
    v = b"any"
    tid = token_id(v, KEY, length_bytes=TOKEN_ID_LENGTH_BYTES)
    decoded = base64.urlsafe_b64decode(tid + "=" * (4 - len(tid) % 4))
    assert len(decoded) == TOKEN_ID_LENGTH_BYTES
