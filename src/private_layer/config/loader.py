"""Load config from YAML with deep-merge (single file, no tenants)."""
import copy
from pathlib import Path
from typing import Any, Dict

import yaml

from private_layer.config.labels import DEFAULT_LABELS
from private_layer.config.schema import Config, OutputOptions, TokenizationSettings
from private_layer.exceptions import ConfigError


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


DEFAULT_REGEX_RULES: Dict[str, Dict[str, str]] = {
    "email": {"pattern": r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"},
    "phone": {
        "pattern": r"(?<!\d)(?:\+\d{1,3}\s?)?(?:\(\d{2,4}\)\s?)?[\d\-\s]{6,15}(?!\d)"
    },
    "iban": {"pattern": r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"},
    "credit_card": {"pattern": r"\b(?:\d[ -]*?){13,19}\b"},
    "ip": {
        "pattern": r"\b(?:(?:2(?:5[0-5]|[0-4]\d))|(?:1?\d?\d))(?:\.(?:2(?:5[0-5]|[0-4]\d)|1?\d?\d)){3}\b"
    },
}


def load_config(path: Path) -> Config:
    """Load config from YAML; merge with defaults."""
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return config_from_dict(raw)


def config_from_dict(raw: Dict[str, Any]) -> Config:
    """Build Config from dict (defaults + deep_merge)."""
    defaults = {
        "detector_type": "regex",
        "labels": DEFAULT_LABELS,
        "threshold": 0.5,
        "per_label_thresholds": {},
        "regex_rules": DEFAULT_REGEX_RULES,
        "local_model_name": None,
        "gliner_model": None,
        "spacy_model": None,
        "flair_model": None,
        "transformers_model": None,
        "presidio_language": None,
        "presidio_entities": None,
        "scrubadub_locale": None,
        "tokenization": {
            "placeholder_format": "[PII_{i}]",
            "immutable": True,
            "include_hash": False,
        },
        "output": {"include_mapping": True},
    }
    merged = deep_merge(defaults, raw)
    tok = merged.get("tokenization", {})
    out = merged.get("output", {})
    return Config(
        detector_type=str(merged.get("detector_type", "regex")),
        labels=list(merged.get("labels", [])),
        threshold=float(merged.get("threshold", 0.5)),
        per_label_thresholds={
            k.strip().lower(): float(v)
            for k, v in (merged.get("per_label_thresholds") or {}).items()
        },
        regex_rules=merged.get("regex_rules") or {},
        local_model_name=merged.get("local_model_name"),
        gliner_model=merged.get("gliner_model"),
        spacy_model=merged.get("spacy_model"),
        flair_model=merged.get("flair_model"),
        transformers_model=merged.get("transformers_model"),
        presidio_language=merged.get("presidio_language"),
        presidio_entities=merged.get("presidio_entities"),
        scrubadub_locale=merged.get("scrubadub_locale"),
        tokenization=TokenizationSettings(
            placeholder_format=tok.get("placeholder_format", "[PII_{i}]"),
            immutable=tok.get("immutable", True),
            include_hash=tok.get("include_hash", False),
        ),
        output=OutputOptions(include_mapping=out.get("include_mapping", True)),
    )


def default_config() -> Config:
    """Return default in-memory config (no file)."""
    return config_from_dict({})
