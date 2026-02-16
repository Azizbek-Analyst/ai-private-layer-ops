# Architecture

## Overview

AI Private Layer is a **developer tool** (SDK + CLI) for PII detection and tokenization. No server; it provides:

- **detect(text)** → list of spans (half-open `[start, end)`)
- **protect(text)** → masked text with placeholders `[PII_1]`, `[PII_2]`, … and a reversible mapping
- **restore(masked_text, mapping)** → original text

Placeholders are immutable tokens. The mapping is JSON-serializable and must not be logged (contains PII).

## Pipeline

1. **Detect** — Run the configured detector (regex, local model, ner, presidio, spacy, flair, transformers, scrubadub) to get candidate spans.
2. **Resolve overlaps** — Deterministic: sort by start, then by length (prefer longer), then by source priority (configurable).
3. **Replace** — Sort spans by start descending; replace each span with a placeholder to avoid index shift. Build mapping (placeholder → label, original_text, start, end, optional hash).
4. **Restore** — Replace placeholders in masked text using the mapping.

## Detectors

- **RegexDetector** — Built-in; uses compiled regex rules from config. No extra deps.
- **LocalModelDetector** — Loads from `detectors/models/{name}`. Tries bare load (transformers only); falls back to optional NER library. Install: `pip install ai-private-layer[local_model]`. Use CLI: `-d --local-model NAME`.
- **GLiNERDetector** (detector_type `ner`) — NER model from Hugging Face or local path. Install: `pip install ai-private-layer[local_model]`.
- **PresidioDetector**, **SpacyDetector**, **FlairDetector**, **TransformersDetector**, **ScrubadubSpacyDetector** — Optional; install the corresponding extra.

## Config

Single file (e.g. `config.yml`): `detector_type`, `local_model_name`, `labels`, `threshold`, `per_label_thresholds`, `regex_rules`, `tokenization`, `output`. No tenants; deep-merge with defaults. See [config_reference.md](config_reference.md).

## Security

- Mapping contains original PII; treat as sensitive. Do not log mapping entries.
- Encryption is optional (`pip install -e ".[crypto]"`); core value is tokenization + mapping.
