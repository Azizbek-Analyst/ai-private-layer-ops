"""Stream JSONL for dataset protect (line-by-line, no full load)."""
import json
from pathlib import Path
from typing import Any

from private_layer.core import protect, restore
from private_layer.core.types import MappingEntry
from private_layer.config import Config, default_config, load_config


def stream_protect(
    input_path: Path,
    output_path: Path,
    text_field: str = "text",
    config: Config | None = None,
    config_path: Path | None = None,
    include_mapping: bool = False,
) -> int:
    """
    Read JSONL from input_path, protect text_field on each line, write to output_path.
    Returns number of lines processed.
    """
    cfg = config or (load_config(config_path) if config_path else default_config())
    count = 0
    with input_path.open("r", encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            raw = line
            line = line.strip()
            if not line:
                fout.write(raw if raw.endswith("\n") else "\n")
                count += 1
                continue
            obj = json.loads(line)
            text = obj.get(text_field, "")
            if not text:
                fout.write(line + "\n")
                count += 1
                continue
            result = protect(text, config=cfg)
            out_obj: dict[str, Any] = {**obj, text_field: result.masked_text}
            if include_mapping:
                out_obj["_mapping"] = [e.to_dict() for e in result.mapping]
            fout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")
            count += 1
    return count


def stream_restore(
    input_path: Path,
    output_path: Path,
    text_field: str = "text",
    mapping_field: str = "_mapping",
) -> int:
    """Restore text_field using mapping_field in each JSONL line."""
    count = 0
    with input_path.open("r", encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for line in fin:
            line = line.strip()
            if not line:
                fout.write("\n")
                count += 1
                continue
            obj = json.loads(line)
            text = obj.get(text_field, "")
            raw_mapping = obj.get(mapping_field, [])
            mapping = [
                MappingEntry.from_dict(e) if isinstance(e, dict) else e
                for e in raw_mapping
            ]
            restored = restore(text, mapping)
            out_obj = {**obj, text_field: restored}
            out_obj.pop(mapping_field, None)
            fout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")
            count += 1
    return count
