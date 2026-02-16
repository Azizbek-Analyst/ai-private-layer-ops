"""Overlap resolution is deterministic."""
from private_layer.core.types import Span
from private_layer.tokenization.span_ops import resolve_overlaps


def test_no_overlap():
    spans = [
        Span(0, 5, "a", source="regex"),
        Span(10, 15, "b", source="regex"),
    ]
    out = resolve_overlaps(spans)
    assert len(out) == 2
    assert out[0].start == 0 and out[0].end == 5
    assert out[1].start == 10 and out[1].end == 15


def test_overlap_prefer_longer():
    # [0,10) and [5,12) -> keep longer [0,10) then add [5,12) would overlap; we keep longer
    spans = [
        Span(0, 10, "x", source="regex"),
        Span(5, 12, "y", source="model"),
    ]
    out = resolve_overlaps(spans, prefer_longer=True, source_priority={"regex": 0, "model": 1})
    assert len(out) == 1
    # Longer is [5,12) length 7 vs [0,10) length 10 -> keep [0,10)
    assert out[0].start == 0 and out[0].end == 10


def test_overlap_deterministic_order():
    spans = [
        Span(0, 3, "a", source="regex"),
        Span(1, 4, "b", source="regex"),
    ]
    out = resolve_overlaps(spans)
    assert len(out) == 1
    # Same length; first by start wins then replaced by second (overlap). Prefer longer: same length -> keep first
    assert out[0].end - out[0].start == 3
