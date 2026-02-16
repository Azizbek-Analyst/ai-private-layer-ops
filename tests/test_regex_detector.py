"""RegexDetector detects emails and phones."""
from private_layer.config import default_config
from private_layer.detectors import RegexDetector
from private_layer.core.types import Span


def test_regex_detects_email():
    cfg = default_config()
    det = RegexDetector(cfg)
    text = "Send to john.doe@example.com please."
    result = det.detect(text)
    assert len(result.spans) >= 1
    email_span = next(s for s in result.spans if "john.doe@example.com" in text[s.start:s.end])
    assert email_span.label == "email"


def test_regex_detects_phone():
    cfg = default_config()
    det = RegexDetector(cfg)
    text = "Call +1 (415) 555-0199."
    result = det.detect(text)
    assert len(result.spans) >= 1
    phone_span = next((s for s in result.spans if s.label == "phone"), None)
    assert phone_span is not None


def test_regex_returns_half_open_spans():
    cfg = default_config()
    det = RegexDetector(cfg)
    text = "a@b.co"
    result = det.detect(text)
    assert len(result.spans) == 1
    s = result.spans[0]
    assert text[s.start:s.end] == "a@b.co"
    assert s.end - s.start == 6
