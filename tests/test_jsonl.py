"""JSONL dataset protect runs streaming and outputs expected keys."""
import json
import tempfile
from pathlib import Path

import pytest
from private_layer.io import stream_protect, stream_restore


def test_stream_protect():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps({"text": "Email me at x@y.com", "id": 1}) + "\n")
        f.write(json.dumps({"text": "No PII here", "id": 2}) + "\n")
        input_path = Path(f.name)
    output_path = Path(tempfile.mktemp(suffix=".jsonl"))
    try:
        n = stream_protect(
            input_path=input_path,
            output_path=output_path,
            text_field="text",
            include_mapping=False,
        )
        assert n == 2
        lines = output_path.read_text().strip().split("\n")
        assert len(lines) == 2
        o1 = json.loads(lines[0])
        assert "text" in o1
        assert o1["text"] != "Email me at x@y.com"
        assert "[PII_" in o1["text"]
        assert o1["id"] == 1
        o2 = json.loads(lines[1])
        assert o2["text"] == "No PII here"
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)


def test_stream_protect_with_mapping():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write(json.dumps({"text": "x@y.com"}) + "\n")
        input_path = Path(f.name)
    output_path = Path(tempfile.mktemp(suffix=".jsonl"))
    try:
        stream_protect(
            input_path=input_path,
            output_path=output_path,
            text_field="text",
            include_mapping=True,
        )
        lines = output_path.read_text().strip().split("\n")
        o = json.loads(lines[0])
        assert "_mapping" in o
        assert len(o["_mapping"]) >= 1
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
