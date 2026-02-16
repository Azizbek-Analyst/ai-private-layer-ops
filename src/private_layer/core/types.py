"""Core types for detection and protection pipeline."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Span:
    """Half-open span [start, end)."""
    start: int
    end: int
    label: str
    score: Optional[float] = None
    source: Optional[str] = None  # "regex" | "model"

    def length(self) -> int:
        return self.end - self.start


@dataclass
class DetectionResult:
    """Result of detect(): list of spans."""
    spans: List[Span]
    raw_entities: Optional[List[Dict[str, Any]]] = None  # optional for debugging


@dataclass
class MappingEntry:
    """One placeholder -> original. JSON-serializable."""
    placeholder: str
    label: str
    original_text: str
    start: int
    end: int
    hash: Optional[str] = None  # optional hash of original_text

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "placeholder": self.placeholder,
            "label": self.label,
            "original_text": self.original_text,
            "start": self.start,
            "end": self.end,
        }
        if self.hash is not None:
            d["hash"] = self.hash
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MappingEntry":
        return cls(
            placeholder=d["placeholder"],
            label=d["label"],
            original_text=d["original_text"],
            start=int(d["start"]),
            end=int(d["end"]),
            hash=d.get("hash"),
        )


@dataclass
class ProtectedText:
    """Result of protect(): masked text + mapping + entities."""
    masked_text: str
    mapping: List[MappingEntry]
    entities: List[Span]  # resolved spans that were replaced

    def to_dict(self) -> Dict[str, Any]:
        return {
            "masked_text": self.masked_text,
            "mapping": [e.to_dict() for e in self.mapping],
            "entities": [
                {"start": s.start, "end": s.end, "label": s.label}
                for s in self.entities
            ],
        }
