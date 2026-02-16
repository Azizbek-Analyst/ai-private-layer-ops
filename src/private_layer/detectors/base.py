"""Detector interface."""
from abc import ABC, abstractmethod

from private_layer.core.types import DetectionResult


class Detector(ABC):
    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Return detected spans (half-open [start, end))."""
        ...
