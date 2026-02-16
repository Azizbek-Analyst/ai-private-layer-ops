"""Top-level pipeline: detect, protect, restore."""
from pathlib import Path
from typing import Optional

from private_layer.config import Config, default_config, load_config
from private_layer.core.types import DetectionResult, MappingEntry, ProtectedText, Span
from private_layer.detectors import get_detector
from private_layer.tokenization.mapper import build_mapping, restore_text
from private_layer.tokenization.span_ops import resolve_overlaps


def detect(
    text: str,
    config: Optional[Config] = None,
    config_path: Optional[Path] = None,
) -> DetectionResult:
    """Detect PII spans. Uses config from config_path or in-memory config."""
    if config is None:
        if config_path and Path(config_path).exists():
            config = load_config(Path(config_path))
        else:
            config = default_config()
    detector = get_detector(config)
    result = detector.detect(text)
    # Resolve overlaps
    resolved = resolve_overlaps(result.spans)
    return DetectionResult(spans=resolved, raw_entities=result.raw_entities)


def protect(
    text: str,
    config: Optional[Config] = None,
    config_path: Optional[Path] = None,
) -> ProtectedText:
    """
    Detect spans, resolve overlaps, replace with placeholders, return masked text + mapping.
    """
    det = detect(text, config=config, config_path=config_path)
    cfg = config or (load_config(config_path) if config_path and Path(config_path).exists() else default_config())
    ph_fmt = cfg.tokenization.placeholder_format
    include_hash = cfg.tokenization.include_hash
    masked, mapping = build_mapping(text, det.spans, ph_fmt, include_hash)
    return ProtectedText(
        masked_text=masked,
        mapping=mapping,
        entities=det.spans,
    )


def restore(
    masked_text: str,
    mapping: list[MappingEntry],
) -> str:
    """Restore original text from masked text and mapping."""
    return restore_text(masked_text, mapping)
