"""Local model detector: loads from detectors/models/{name}. No engine name exposed to CLI."""
from pathlib import Path
from typing import Any, Dict

from private_layer.config.labels import DEFAULT_LABELS, field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span
from private_layer.exceptions import ConfigError

from .base import Detector

_MODEL_CACHE: Dict[str, Any] = {}


class LocalModelDetector(Detector):
    """Load model from detectors/models/{local_model_name}. Uses same NER logic as other model detectors."""

    def __init__(self, config: Config) -> None:
        name = (config.local_model_name or "").strip()
        if not name:
            raise ConfigError("local_model_name is required when using local model (e.g. -d --local-model private-layer-v1)")
        models_dir = Path(__file__).resolve().parent / "models"
        model_path = models_dir / name
        if not model_path.is_dir():
            raise ConfigError(
                f"Local model {name!r} not found at {model_path}. "
                f"Run scripts/download_gliner_model.py to create detectors/models/{name}/"
            )
        try:
            from gliner import GLiNER
        except ImportError as e:
            raise ImportError(
                "Local model requires: pip install ai-private-layer[gliner]"
            ) from e
        path_str = str(model_path)
        if path_str not in _MODEL_CACHE:
            _MODEL_CACHE[path_str] = GLiNER.from_pretrained(path_str, local_files_only=True)
        self._model = _MODEL_CACHE[path_str]
        self._labels = config.labels or list(DEFAULT_LABELS)
        self._threshold = config.threshold
        self._per_label = config.per_label_thresholds or {}

    def detect(self, text: str) -> DetectionResult:
        entities = self._model.predict_entities(
            text, self._labels, threshold=self._threshold
        )
        spans: list[Span] = []
        for ent in entities:
            start = int(ent.get("start", 0))
            end = int(ent.get("end", 0))
            if end <= start:
                continue
            label = ent.get("label", "")
            field = field_of(label)
            score = float(ent.get("score", 0))
            norm = label.strip().lower()
            th = self._per_label.get(norm) or self._per_label.get(field) or self._threshold
            if score < th:
                continue
            spans.append(
                Span(
                    start=start,
                    end=end,
                    label=field,
                    score=score,
                    source="model",
                )
            )
        return DetectionResult(spans=spans)
