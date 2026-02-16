"""Dataset demo: create a small JSONL, run stream_protect, then stream_restore."""
import json
import tempfile
from pathlib import Path
from private_layer.io import stream_protect, stream_restore

def main():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for i, line in enumerate([
            {"id": 1, "text": "Email alice@test.com and bob@test.com."},
            {"id": 2, "text": "No PII in this line."},
        ]):
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
        input_path = Path(f.name)

    out_path = Path(tempfile.mktemp(suffix=".jsonl"))
    out2_path = Path(tempfile.mktemp(suffix=".jsonl"))
    try:
        n = stream_protect(input_path, out_path, text_field="text", include_mapping=True)
        print(f"Protected {n} lines -> {out_path}")
        with out_path.open() as f:
            for line in f:
                print(line.strip()[:80] + "…" if len(line) > 80 else line.strip())

        n2 = stream_restore(out_path, out2_path, text_field="text", mapping_field="_mapping")
        print(f"Restored {n2} lines -> {out2_path}")
    finally:
        input_path.unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)
        out2_path.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
