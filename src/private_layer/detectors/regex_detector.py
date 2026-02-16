"""Regex-based PII detector (no heavy deps)."""
import re
from typing import Any, Dict

from private_layer.config.schema import Config
from private_layer.core.types import DetectionResult, Span

from .base import Detector


def _normalize_key(val: str) -> str:
    return val.strip().lower()


def compile_regex_rules(rules: Dict[str, Any]) -> Dict[str, re.Pattern]:
    """Compile regex_rules (label -> pattern string or {pattern: ...}) to compiled regexes."""
    compiled: Dict[str, re.Pattern] = {}
    for label, rule in (rules or {}).items():
        pattern = None
        if isinstance(rule, dict):
            pattern = rule.get("pattern")
        elif isinstance(rule, str):
            pattern = rule
        if pattern:
            compiled[label] = re.compile(pattern)
    return compiled


class RegexDetector(Detector):
    """Built-in regex detector."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._compiled = compile_regex_rules(config.regex_rules)

    def detect(self, text: str) -> DetectionResult:
        spans: list[Span] = []
        for label, pattern in self._compiled.items():
            field = _normalize_key(label)
            for m in pattern.finditer(text):
                start, end = m.span()
                if end <= start:
                    continue
                spans.append(
                    Span(
                        start=start,
                        end=end,
                        label=field,
                        score=None,
                        source="regex",
                    )
                )
        return DetectionResult(spans=spans)
