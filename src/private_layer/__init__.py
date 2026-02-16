"""
AI Private Layer — PII detection and tokenization as a Developer Tool (SDK + CLI).

One-line: Detect PII, replace with immutable placeholders, keep a mapping to restore.
"""
from private_layer.config import Config, default_config, load_config
from private_layer.core import (
    detect,
    protect,
    restore,
    DetectionResult,
    MappingEntry,
    ProtectedText,
    Span,
    ConfigError,
    DetectorError,
    PrivateLayerError,
)

__version__ = "0.1.0"
__all__ = [
    "Config",
    "default_config",
    "load_config",
    "detect",
    "protect",
    "restore",
    "DetectionResult",
    "MappingEntry",
    "ProtectedText",
    "Span",
    "ConfigError",
    "DetectorError",
    "PrivateLayerError",
]
