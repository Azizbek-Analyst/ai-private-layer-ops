#!/usr/bin/env python3
"""
Download the default NER model and save it to detectors/models/private-layer-v1.
After running, use: private-layer detect "text" -d --local-model private-layer-v1

Run from repo root:
  pip install -e ".[local_model]"
  python scripts/download_model.py

Creates: src/private_layer/detectors/models/private-layer-v1/
"""
from pathlib import Path


def main() -> None:
    try:
        from gliner import GLiNER
    except ImportError:
        print("Install the local model extra first: pip install -e \".[local_model]\"")
        raise SystemExit(1)

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = repo_root / "src" / "private_layer" / "detectors" / "models" / "private-layer-v1"
    out_dir.mkdir(parents=True, exist_ok=True)

    model_id = "urchade/gliner_multi-v2.1"
    print(f"Downloading {model_id} ...")
    model = GLiNER.from_pretrained(model_id)
    print(f"Saving to {out_dir} ...")
    model.save_pretrained(str(out_dir))
    print("Done. Use: private-layer detect \"text\" -d --local-model private-layer-v1")


if __name__ == "__main__":
    main()
