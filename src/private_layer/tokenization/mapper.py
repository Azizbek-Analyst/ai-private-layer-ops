"""Build mapping from spans and restore text from masked text + mapping."""
import hashlib
from typing import List, Optional

from private_layer.core.types import MappingEntry, Span
from private_layer.tokenization.placeholders import (
    DEFAULT_PLACEHOLDER_PATTERN,
    format_placeholder,
    parse_placeholder_pattern,
)
from private_layer.tokenization.span_ops import replacement_order


def build_mapping(
    text: str,
    spans: List[Span],
    placeholder_format: Optional[str] = None,
    include_hash: bool = False,
) -> tuple[str, List[MappingEntry]]:
    """
    Replace spans in text with placeholders [PII_1], [PII_2], ...
    Returns (masked_text, mapping). Replacement order: by start descending.
    """
    if not spans:
        return text, []
    ordered = replacement_order(spans)
    masked = text
    mapping: List[MappingEntry] = []
    for i, span in enumerate(ordered, start=1):
        ph = format_placeholder(i, placeholder_format)
        raw = masked[span.start : span.end]
        h = hashlib.sha256(raw.encode()).hexdigest()[:16] if include_hash else None
        mapping.append(
            MappingEntry(
                placeholder=ph,
                label=span.label,
                original_text=raw,
                start=span.start,
                end=span.end,
                hash=h,
            )
        )
        masked = masked[: span.start] + ph + masked[span.end :]
    # Mapping order: by appearance in original text (by start)
    mapping.sort(key=lambda e: e.start)
    return masked, mapping


def apply_mapping(
    text: str,
    spans: List[Span],
    placeholder_format: Optional[str] = None,
    include_hash: bool = False,
) -> tuple[str, List[MappingEntry]]:
    """Alias for build_mapping for clarity."""
    return build_mapping(text, spans, placeholder_format, include_hash)


def restore_text(
    masked_text: str,
    mapping: List[MappingEntry],
    pattern: Optional[str] = None,
) -> str:
    """
    Restore original text from masked_text by replacing placeholders
    using mapping (list of MappingEntry or dicts with placeholder, original_text).
    """
    if not mapping:
        return masked_text
    # Build placeholder -> original
    by_ph: dict[str, str] = {}
    for e in mapping:
        if isinstance(e, dict):
            by_ph[e["placeholder"]] = e["original_text"]
        else:
            by_ph[e.placeholder] = e.original_text
    rx = parse_placeholder_pattern(pattern)

    def repl(m):
        idx = m.group(1)
        ph = f"[PII_{idx}]"
        return by_ph.get(ph, m.group(0))

    return rx.sub(repl, masked_text)
