"""Shared exceptions (no internal imports to avoid cycles)."""


class PrivateLayerError(Exception):
    """Base exception."""


class ConfigError(PrivateLayerError):
    """Invalid or missing configuration."""


class DetectorError(PrivateLayerError):
    """Detector failed (e.g. model not installed)."""
