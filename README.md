# AI Private Layer

PII detection and tokenization: replace sensitive text with placeholders and a reversible mapping (SDK + CLI, no server).

## Quick start

```bash
pip install -e .
private-layer protect "Email me at john@example.com or call +1 555 123 4567."
```

Output: `masked_text` with `[PII_1]`, `[PII_2]`, … and a `mapping` to restore.

## Installing dependencies

- **Base (regex only):** `pip install -e .`
- **Local model (recommended):** `pip install -e ".[gliner]"` then run `python scripts/download_gliner_model.py` once to create `detectors/models/private-layer-v1/`
- **Other detectors:** `pip install -e ".[presidio]"`, `.[spacy]`, `.[flair]`, `.[transformers_ner]`, `.[scrubadub]`
- **Encryption:** `pip install -e ".[crypto]"`
- **Tests:** `pip install -e ".[dev]"`

All dependencies are in **pyproject.toml**.

## Local model (no engine name in CLI)

Models live under `src/private_layer/detectors/models/`. One-time setup:

```bash
pip install -e ".[gliner]"
python scripts/download_gliner_model.py
```

Then use `-d` (use local model) and `--local-model NAME`:

```bash
private-layer detect "John lives in Berlin" -d --local-model private-layer-v1
private-layer protect "text" -d --local-model private-layer-v1
```

For other detectors use `--detector` / `-p`: e.g. `-p presidio`, `-p spacy`.

## SDK

```python
from private_layer import detect, protect, restore

r = protect("Contact jane@example.com")
print(r.masked_text)   # "Contact [PII_1]"
original = restore(r.masked_text, r.mapping)
print(original == "Contact jane@example.com")
```

- **detect(text, config=None)** → spans
- **protect(text, ...)** → masked_text, mapping
- **restore(masked_text, mapping)** → str

## CLI

| Command | Description |
|---------|-------------|
| `detect TEXT` | Print detected PII spans |
| `protect TEXT` | Mask text, output mapping |
| `restore MASKED MAPPING_JSON` | Restore original text |
| `protect TEXT --encrypt` | Mask + encrypt (bundles for decrypt) |
| `decrypt MASKED BUNDLES_JSON` | Decrypt and restore |
| `dataset protect -i in.jsonl -o out.jsonl` | Protect `text` field in JSONL |

Options: `-c` config, `-d --local-model NAME` (local model), `-p` detector type (presidio, spacy, …), `-f` json|text.

## Config

Single YAML: `detector_type`, regex rules, thresholds. See `config.example.yml` and [docs/config_reference.md](docs/config_reference.md). If `--config` path does not exist, default (regex) is used.

## Encryption (optional)

```bash
pip install -e ".[crypto]"
export TOKEN_KEY_HEX=$(openssl rand -hex 32)
private-layer protect "Email john@example.com" --encrypt
private-layer decrypt "Email [EMAIL_xxx]" "$(jq -c '.bundles' out.json)"
```

## Docs

- [Config reference](docs/config_reference.md)
- [Architecture](docs/architecture.md)
- [Threat model](docs/threat_model.md)

## Run examples

From repo root (after `pip install -e .` or `pip install -e ".[gliner]"` for local model):

```bash
# Help
private-layer --help
private-layer detect --help

# Regex (default): detect and protect
private-layer detect "Email me at john@example.com or +1 555 123 4567" --format text
private-layer protect "Email me at john@example.com"

# Local model (after: pip install -e ".[gliner]" && python scripts/download_gliner_model.py)
private-layer detect "John lives in Berlin" -d --local-model private-layer-v1
private-layer protect "John lives in Berlin" -d --local-model private-layer-v1 --format text

# Other detectors (install the extra first, e.g. pip install -e ".[presidio]")
private-layer detect "Hi, I am Jane Doe" -p presidio
private-layer detect "John in Berlin" -p spacy --format text

# Restore from mapping
private-layer restore 'Contact [PII_1]' '[{"placeholder":"[PII_1]","label":"email","original_text":"jane@example.com"}]'

# JSONL
echo '{"text":"Email alice@test.com"}' > in.jsonl
private-layer dataset protect -i in.jsonl -o out.jsonl -d --local-model private-layer-v1
cat out.jsonl
```

If `private-layer` is not in PATH:

```bash
PYTHONPATH=src python -m private_layer detect "text"
```

Python examples: `examples/quickstart.py`, `examples/dataset_demo.py`.

## License

Apache-2.0
