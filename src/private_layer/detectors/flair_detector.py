"""Flair NER detector. Requires: pip install ai-private-layer[flair]."""
from typing import List

from private_layer.config.labels import field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


class FlairDetector(Detector):
    """Flair NER (e.g. 'ner' or 'ner-fast')."""

    def __init__(self, config: Config) -> None:
        try:
            from flair.data import Sentence
            from flair.nn import Classifier
        except ImportError as e:
            raise ImportError(
                "Flair not installed. Install with: pip install ai-private-layer[flair]"
            ) from e
        self._config = config
        model = (config.flair_model or "ner").strip()
        self._Classifier = Classifier
        self._Sentence = Sentence
        self._tagger = Classifier.load(model)

    def detect(self, text: str) -> DetectionResult:
        sentence = self._Sentence(text)
        self._tagger.predict(sentence)
        spans: List[Span] = []
        for span in sentence.get_spans("ner"):
            # Flair uses token indices; convert to character offsets
            start_tok = span.tokens[0]
            end_tok = span.tokens[-1]
            start = start_tok.start_position
            end = end_tok.end_position
            if end <= start:
                continue
            label = span.tag if hasattr(span, "tag") else (span.labels[0].value if span.labels else "unknown")
            field = field_of(label)
            score = float(span.score) if hasattr(span, "score") and span.score is not None else None
            spans.append(
                Span(start=start, end=end, label=field, score=score, source="flair")
            )
        return DetectionResult(spans=spans)
