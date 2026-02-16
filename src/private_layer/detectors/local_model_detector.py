"""Local model detector: loads from detectors/models/{name}. No engine name exposed to CLI.

Supports two loading modes:
1. Bare load: transformers.AutoTokenizer + AutoModel.from_pretrained(..., trust_remote_code=True).
   Model dir must contain tokenizer files and config.json. The loaded model is used if it has predict_entities().
2. Fallback: optional NER library for checkpoints from the download script.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from private_layer.config.labels import DEFAULT_LABELS, field_of
from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span
from private_layer.exceptions import ConfigError

from .base import Detector

_MODEL_CACHE: Dict[str, Any] = {}


def _load_bare(model_path: Path) -> tuple[Any, Any] | None:
    """Load with transformers + torch only. Returns (tokenizer, model) or None if not possible."""
    try:
        from transformers import AutoModel, AutoTokenizer
    except ImportError:
        return None
    path_str = str(model_path)
    if not (model_path / "config.json").exists() and not (model_path / "gliner_config.json").exists():
        return None
    config_path = model_path / "config.json"
    if not config_path.exists():
        return None
    try:
        tokenizer = AutoTokenizer.from_pretrained(path_str, local_files_only=True)
        with open(config_path, encoding="utf-8") as f:
            json.load(f)  # validate config exists
        model = AutoModel.from_pretrained(
            path_str,
            local_files_only=True,
            trust_remote_code=True,
        )
        model.eval()
        return (tokenizer, model)
    except Exception:
        return None


def _load_ner_fallback(model_path: Path) -> Any:
    """Load with optional NER library (for checkpoints from download script)."""
    from gliner import GLiNER
    return GLiNER.from_pretrained(str(model_path), local_files_only=True)


def _apply_tokenizer_extra_special_tokens_workaround() -> None:
    """Work around transformers expecting extra_special_tokens as dict, not list."""
    try:
        from transformers import tokenization_utils_base
    except ImportError:
        return
    base = tokenization_utils_base.PreTrainedTokenizerBase
    if getattr(base, "_private_layer_patched_extra_special", False):
        return
    _original = base._set_model_specific_special_tokens

    def _patched(self: Any, special_tokens: Any) -> None:
        if isinstance(special_tokens, list):
            self._special_tokens_map["additional_special_tokens"] = special_tokens
            return
        _original(self, special_tokens)

    base._set_model_specific_special_tokens = _patched
    base._private_layer_patched_extra_special = True  # type: ignore[attr-defined]


def _entities_from_model(
    model: Any,
    text: str,
    labels: List[str],
    threshold: float,
    per_label: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Call model.predict_entities if available; otherwise return [] (bare AutoModel has no NER)."""
    if hasattr(model, "predict_entities") and callable(getattr(model, "predict_entities")):
        return model.predict_entities(text, labels, threshold=threshold) or []
    return []


class LocalModelDetector(Detector):
    """Load model from detectors/models/{local_model_name}.
    Tries bare load (transformers only); falls back to optional NER library for standard checkpoints.
    """

    def __init__(self, config: Config) -> None:
        name = (config.local_model_name or "").strip()
        if not name:
            raise ConfigError("local_model_name is required when using local model (e.g. -d --local-model private-layer-v1)")
        models_dir = Path(__file__).resolve().parent / "models"
        model_path = models_dir / name
        if not model_path.is_dir():
            raise ConfigError(
                f"Local model {name!r} not found at {model_path}. "
                f"Run scripts/download_model.py to create detectors/models/{name}/"
            )
        path_str = str(model_path)
        if path_str not in _MODEL_CACHE:
            # 1) Try bare load: AutoTokenizer + AutoModel.from_pretrained(..., trust_remote_code=True)
            bare = _load_bare(model_path)
            if bare is not None:
                _tokenizer, model = bare
                if hasattr(model, "predict_entities") and callable(getattr(model, "predict_entities")):
                    _MODEL_CACHE[path_str] = model
                else:
                    _apply_tokenizer_extra_special_tokens_workaround()
                    _MODEL_CACHE[path_str] = _load_ner_fallback(model_path)
            else:
                _apply_tokenizer_extra_special_tokens_workaround()
                _MODEL_CACHE[path_str] = _load_ner_fallback(model_path)
        self._model = _MODEL_CACHE[path_str]
        self._labels = config.labels or list(DEFAULT_LABELS)
        self._threshold = config.threshold
        self._per_label = config.per_label_thresholds or {}

    def detect(self, text: str) -> DetectionResult:
        entities = _entities_from_model(
            self._model,
            text,
            self._labels,
            self._threshold,
            self._per_label,
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
