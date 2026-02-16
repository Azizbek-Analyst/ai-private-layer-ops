"""protect -> restore roundtrip equals original."""
import pytest
from private_layer import protect, restore


def test_roundtrip_basic():
    text = "Contact john.doe@example.com or +1 415 555 0199."
    result = protect(text)
    assert result.masked_text != text
    restored = restore(result.masked_text, result.mapping)
    assert restored == text


def test_roundtrip_no_pii():
    text = "Hello world."
    result = protect(text)
    assert result.masked_text == text
    assert result.mapping == []
    assert restore(text, []) == text


def test_roundtrip_multiple():
    text = "Email: a@b.co and b@c.com and phone 1234567890."
    result = protect(text)
    restored = restore(result.masked_text, result.mapping)
    assert restored == text
