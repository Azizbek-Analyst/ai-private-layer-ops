# Architecture

## Overview

AI Private Layer is a **developer tool** (SDK + CLI) for PII detection and tokenization. It does not run a server; it provides:

- **detect(text)** → list of spans (half-open `[start, end)`)
- **protect(text)** → masked text with placeholders `[PII_1]`, `[PII_2]`, ... and a reversible mapping
- **restore(masked_text, mapping)** → original text

Placeholders are immutable tokens. The mapping is JSON-serializable and must not log raw PII.

## Pipeline

1. **Detect** — Run configured detector (regex and/or GLiNER) to get candidate spans.
2. **Resolve overlaps** — Deterministic: sort by start, then by length (prefer longer), then by source priority (e.g. regex over model or configurable).
3. **Replace** — Sort spans by start descending; replace each span with a placeholder to avoid index shift. Build mapping (placeholder → label, original_text, start, end, optional hash).
4. **Restore** — Replace placeholders in masked text using the mapping.

## Detectors

- **RegexDetector** — Built-in; uses compiled regex rules from config. No extra deps.
- **GLiNERDetector** — Optional; install with `pip install ai-private-layer[gliner]`. Uses a cached model and label/threshold config.

## Config

Single file (e.g. `config.yml`): `detector_type`, `labels`, `threshold`, `per_label_thresholds`, `regex_rules`, `tokenization`, `output`. No tenants; deep-merge with defaults.

## Security

- Mapping contains original PII; treat it as sensitive. Do not log mapping entries.
- Encryption is **optional** and demo-level (e.g. `crypto/fernet_encryptor`). Core value is tokenization + mapping.
