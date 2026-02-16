"""Detector registry: get detector by type from config."""
from private_layer.config.schema import Config
from private_layer.exceptions import ConfigError

from .base import Detector
from .regex_detector import RegexDetector

_REGISTRY: dict[str, type] = {
    "regex": RegexDetector,
}


def register_detector(name: str, detector_class: type) -> None:
    _REGISTRY[name] = detector_class


def _load_detector(detector_type: str, config: Config) -> Detector:
    """Lazy-load optional detectors by type."""
    t = detector_type.strip().lower()
    if t == "local":
        try:
            from .local_model_detector import LocalModelDetector
            return LocalModelDetector(config)
        except ImportError as e:
            raise ConfigError(
                "Local model detector requires: pip install ai-private-layer[local_model]"
            ) from e
    if t in ("gliner", "ner"):
        try:
            from .gliner_detector import GLiNERDetector
            return GLiNERDetector(config)
        except ImportError as e:
            raise ConfigError(
                "NER model detector requires: pip install ai-private-layer[local_model]"
            ) from e
    if t == "presidio":
        try:
            from .presidio_detector import PresidioDetector
            return PresidioDetector(config)
        except ImportError as e:
            raise ConfigError(
                "Presidio detector requires: pip install ai-private-layer[presidio]"
            ) from e
    if t in ("spacy", "spacy_trf"):
        try:
            from .spacy_detector import SpacyDetector
            return SpacyDetector(config)
        except ImportError as e:
            raise ConfigError(
                "SpaCy detector requires: pip install ai-private-layer[spacy] or [spacy_trf]"
            ) from e
    if t == "flair":
        try:
            from .flair_detector import FlairDetector
            return FlairDetector(config)
        except ImportError as e:
            raise ConfigError(
                "Flair detector requires: pip install ai-private-layer[flair]"
            ) from e
    if t == "transformers":
        try:
            from .transformers_detector import TransformersDetector
            return TransformersDetector(config)
        except ImportError as e:
            raise ConfigError(
                "Transformers NER detector requires: pip install ai-private-layer[transformers_ner]"
            ) from e
    if t == "scrubadub_spacy":
        try:
            from .scrubadub_detector import ScrubadubSpacyDetector
            return ScrubadubSpacyDetector(config)
        except ImportError as e:
            raise ConfigError(
                "Scrubadub detector requires: pip install ai-private-layer[scrubadub]"
            ) from e
    return None


def get_detector(config: Config) -> Detector:
    """Build detector from config. Optional detectors loaded lazily."""
    t = (config.detector_type or "regex").strip().lower()
    inst = _load_detector(t, config)
    if inst is not None:
        return inst
    if t not in _REGISTRY:
        raise ConfigError(
            f"Unknown detector type: {t!r}. Use: regex, local, ner, presidio, spacy, spacy_trf, flair, transformers, scrubadub_spacy"
        )
    return _REGISTRY[t](config)
