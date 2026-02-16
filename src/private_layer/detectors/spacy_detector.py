"""SpaCy NER detector (en_core_web_sm or en_core_web_trf). Requires: pip install ai-private-layer[spacy] or [spacy_trf]."""
from typing import List

from private_layer.config.labels import field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


class SpacyDetector(Detector):
    """SpaCy NER. Model: en_core_web_sm (small) or en_core_web_trf (transformer)."""

    def __init__(self, config: Config) -> None:
        try:
            import spacy
        except ImportError as e:
            raise ImportError(
                "SpaCy not installed. Install with: pip install ai-private-layer[spacy]"
            ) from e
        self._config = config
        model = (config.spacy_model or "en_core_web_sm").strip()
        try:
            self._nlp = spacy.load(model)
        except OSError:
            raise ImportError(
                f"SpaCy model {model!r} not found. Download with: python -m spacy download {model}"
            )

    def detect(self, text: str) -> DetectionResult:
        doc = self._nlp(text)
        spans: List[Span] = []
        for ent in doc.ents:
            start = ent.start_char
            end = ent.end_char
            if end <= start:
                continue
            field = field_of(ent.label_)
            spans.append(
                Span(start=start, end=end, label=field, score=None, source="spacy")
            )
        return DetectionResult(spans=spans)
