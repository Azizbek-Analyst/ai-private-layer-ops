"""GLiNER-based detector (optional extra)."""
from pathlib import Path
from typing import Any, Dict

from private_layer.config.labels import DEFAULT_LABELS, field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector

# Lazy import and cache (value type: gliner.GLiNER)
_MODEL_CACHE: Dict[str, Any] = {}


def _is_local_model_path(model_name: str) -> bool:
    """True if model_name is an existing local directory (load from file, not Hub)."""
    if not model_name or model_name.startswith(("http://", "https://")):
        return False
    p = Path(model_name)
    return p.exists() and p.is_dir()


class GLiNERDetector(Detector):
    """GLiNER NER detector. Requires: pip install ai-private-layer[gliner].
    Model can be a Hugging Face ID (e.g. urchade/gliner_multi-v2.1) or a local
    directory path (e.g. private-layer-v1 from scripts/download_gliner_model.py).
    Local paths are loaded with local_files_only=True (no network).
    """

    def __init__(self, config: Config) -> None:
        try:
            from gliner import GLiNER
        except ImportError as e:
            raise ImportError(
                "GLiNER not installed. Install with: pip install ai-private-layer[gliner]"
            ) from e
        self._config = config
        self._Gliner = GLiNER
        model_name = (config.gliner_model or "urchade/gliner_multi-v2.1").strip()
        cache_key = str(Path(model_name).resolve()) if _is_local_model_path(model_name) else model_name
        if cache_key not in _MODEL_CACHE:
            if _is_local_model_path(model_name):
                _MODEL_CACHE[cache_key] = GLiNER.from_pretrained(model_name, local_files_only=True)
            else:
                _MODEL_CACHE[cache_key] = GLiNER.from_pretrained(model_name)
        self._model = _MODEL_CACHE[cache_key]
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
