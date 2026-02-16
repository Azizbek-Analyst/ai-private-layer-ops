"""Transformers NER pipeline (e.g. xlm-roberta-finetuned-conll03). Requires: pip install ai-private-layer[transformers_ner]."""
from typing import List

from private_layer.config.labels import field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


class TransformersDetector(Detector):
    """HuggingFace NER pipeline with aggregation_strategy."""

    def __init__(self, config: Config) -> None:
        try:
            from transformers import pipeline
        except ImportError as e:
            raise ImportError(
                "Transformers not installed. Install with: pip install ai-private-layer[transformers_ner]"
            ) from e
        self._config = config
        model = (config.transformers_model or "xlm-roberta-large-finetuned-conll03-english").strip()
        self._pipe = pipeline(
            "ner",
            model=model,
            aggregation_strategy="simple",
        )

    def detect(self, text: str) -> DetectionResult:
        out = self._pipe(text)
        spans: List[Span] = []
        for item in out or []:
            start = item.get("start", 0)
            end = item.get("end", 0)
            if end <= start:
                continue
            label = item.get("entity_group") or item.get("entity", "").lstrip("B-").lstrip("I-")
            field = field_of(label)
            score = item.get("score")
            spans.append(
                Span(start=start, end=end, label=field, score=float(score) if score is not None else None, source="transformers")
            )
        return DetectionResult(spans=spans)
