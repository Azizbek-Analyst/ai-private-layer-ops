"""Placeholder format: default [PII_1], [PII_2], ... immutable tokens."""
import re
from typing import Optional

# Default: [PII_1], [PII_2], ...
DEFAULT_PLACEHOLDER_PATTERN = r"\[PII_(\d+)\]"
DEFAULT_FORMAT = "[PII_{i}]"


def format_placeholder(index: int, fmt: Optional[str] = None) -> str:
    """Produce placeholder string for 1-based index. Default: [PII_1], [PII_2], ..."""
    if fmt is None:
        fmt = DEFAULT_FORMAT
    return fmt.format(i=index)


def parse_placeholder_pattern(pattern: Optional[str] = None) -> re.Pattern:
    """Compiled regex to find placeholders for restore()."""
    if pattern is None:
        pattern = DEFAULT_PLACEHOLDER_PATTERN
    return re.compile(pattern)
