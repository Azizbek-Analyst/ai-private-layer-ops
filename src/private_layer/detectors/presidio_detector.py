"""Presidio-based PII detector. Requires: pip install ai-private-layer[presidio]."""
from typing import List

from private_layer.config.labels import field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


class PresidioDetector(Detector):
    """Uses Microsoft Presidio AnalyzerEngine."""

    def __init__(self, config: Config) -> None:
        try:
            from presidio_analyzer import AnalyzerEngine
        except ImportError as e:
            raise ImportError(
                "Presidio not installed. Install with: pip install ai-private-layer[presidio]"
            ) from e
        self._config = config
        self._engine = AnalyzerEngine()
        self._language = (config.presidio_language or "en").strip().lower()
        self._entities = config.presidio_entities  # None = use engine defaults

    def detect(self, text: str) -> DetectionResult:
        entities = self._engine.analyze(
            text,
            language=self._language,
            entities=self._entities,
        )
        spans: List[Span] = []
        for r in entities:
            start = r.start
            end = r.end
            if end <= start:
                continue
            label = getattr(r, "entity_type", None) or getattr(r, "type", "") or "unknown"
            field = field_of(label)
            spans.append(
                Span(start=start, end=end, label=field, score=getattr(r, "score", None), source="presidio")
            )
        return DetectionResult(spans=spans)
