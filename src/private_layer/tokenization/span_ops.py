"""Span utilities: overlap resolution and replacement order."""
from typing import List, Optional

from private_layer.core.types import Span


def resolve_overlaps(
    spans: List[Span],
    *,
    prefer_longer: bool = True,
    source_priority: Optional[dict] = None,
) -> List[Span]:
    """
    Resolve overlapping spans deterministically.
    - prefer_longer: when overlapping, keep the longer span (default True).
    - source_priority: higher value = preferred (e.g. {"regex": 1, "model": 0}).
    """
    if not spans:
        return []
    if source_priority is None:
        source_priority = {"regex": 1, "model": 0}

    def key(s: Span):
        prio = source_priority.get(s.source or "", 0)
        # start asc, then by length desc, then by source priority desc
        return (s.start, -s.length() if prefer_longer else s.length(), -prio)

    sorted_spans = sorted(spans, key=key)
    resolved: List[Span] = []
    for span in sorted_spans:
        if not resolved or span.start >= resolved[-1].end:
            resolved.append(span)
        else:
            # overlap: keep the one we prefer (longer or higher priority)
            if prefer_longer and span.length() > resolved[-1].length():
                resolved[-1] = span
            elif not prefer_longer and (
                source_priority.get(span.source or "", 0)
                > source_priority.get(resolved[-1].source or "", 0)
            ):
                resolved[-1] = span
    return resolved


def replacement_order(spans: List[Span]) -> List[Span]:
    """Return spans sorted for safe in-place replacement (by start descending)."""
    return sorted(spans, key=lambda s: s.start, reverse=True)
