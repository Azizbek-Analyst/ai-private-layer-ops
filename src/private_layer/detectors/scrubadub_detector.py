"""Scrubadub + SpaCy detector. Requires: pip install ai-private-layer[scrubadub]."""
from typing import List

from private_layer.config.labels import field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


class ScrubadubSpacyDetector(Detector):
    """Scrubadub with SpaCy name/title detector."""

    def __init__(self, config: Config) -> None:
        try:
            import scrubadub
        except ImportError as e:
            raise ImportError(
                "Scrubadub not installed. Install with: pip install ai-private-layer[scrubadub]"
            ) from e
        self._config = config
        locale = (config.scrubadub_locale or "en").strip()
        try:
            import scrubadub_spacy  # noqa: F401
            from scrubadub_spacy.detectors.spacy_name_title import SpacyEntityDetector
            detector = SpacyEntityDetector(locale=locale, model="en_core_web_sm")
            self._scrubber = scrubadub.Scrubber(detector_list=[detector], locale=locale)
        except Exception:
            # Default Scrubber (name, email, etc.) when scrubadub_spacy is not available
            self._scrubber = scrubadub.Scrubber(locale=locale)

    def detect(self, text: str) -> DetectionResult:
        spans: List[Span] = []
        for filth in self._scrubber.iter_filth(text):
            start = getattr(filth, "beg", None) or getattr(filth, "start", 0)
            end = getattr(filth, "end", None) or 0
            if end <= start:
                continue
            kind = getattr(filth, "filth_type", None) or getattr(filth, "type", "unknown")
            if isinstance(kind, str):
                kind = kind.replace(" ", "_").lower()
            field = field_of(kind)
            spans.append(
                Span(start=start, end=end, label=field, score=None, source="scrubadub")
            )
        return DetectionResult(spans=spans)
