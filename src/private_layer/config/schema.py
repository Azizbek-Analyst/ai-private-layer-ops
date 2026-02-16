"""Single config schema: detector, labels, thresholds, regex_rules, tokenization."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TokenizationSettings:
    placeholder_format: str = "[PII_{i}]"
    immutable: bool = True
    include_hash: bool = False


@dataclass
class OutputOptions:
    include_mapping: bool = True


@dataclass
class Config:
    """Single config (no tenants)."""
    detector_type: str = "regex"  # regex | local | gliner | presidio | ...
    labels: List[str] = field(default_factory=list)
    threshold: float = 0.5
    per_label_thresholds: Dict[str, float] = field(default_factory=dict)
    regex_rules: Dict[str, Any] = field(default_factory=dict)  # label -> pattern or {pattern: "..."}
    # Local model (detector_type=local): name of model dir under detectors/models/
    local_model_name: Optional[str] = None
    # GLiNER
    gliner_model: Optional[str] = None
    # SpaCy (spacy / spacy_trf)
    spacy_model: Optional[str] = None  # en_core_web_sm, en_core_web_trf, etc.
    # Flair
    flair_model: Optional[str] = None  # ner, ner-fast, etc.
    # Transformers NER
    transformers_model: Optional[str] = None  # xlm-roberta-large-finetuned-conll03-english, etc.
    # Presidio
    presidio_language: Optional[str] = None  # en, etc.
    presidio_entities: Optional[List[str]] = None  # None = default set
    # Scrubadub SpaCy
    scrubadub_locale: Optional[str] = None  # en
    # Tokenization
    tokenization: TokenizationSettings = field(default_factory=TokenizationSettings)
    output: OutputOptions = field(default_factory=OutputOptions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detector_type": self.detector_type,
            "labels": self.labels,
            "threshold": self.threshold,
            "per_label_thresholds": self.per_label_thresholds,
            "regex_rules": self.regex_rules,
            "local_model_name": self.local_model_name,
            "gliner_model": self.gliner_model,
            "spacy_model": self.spacy_model,
            "flair_model": self.flair_model,
            "transformers_model": self.transformers_model,
            "presidio_language": self.presidio_language,
            "presidio_entities": self.presidio_entities,
            "scrubadub_locale": self.scrubadub_locale,
            "tokenization": {
                "placeholder_format": self.tokenization.placeholder_format,
                "immutable": self.tokenization.immutable,
                "include_hash": self.tokenization.include_hash,
            },
            "output": {"include_mapping": self.output.include_mapping},
        }
