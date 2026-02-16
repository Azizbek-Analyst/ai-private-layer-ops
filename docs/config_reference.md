# Config reference

Single config file (YAML). No tenants.

| Key | Description | Default |
|-----|-------------|---------|
| `detector_type` | `regex`, `local`, `gliner`, `presidio`, `spacy`, `spacy_trf`, `flair`, `transformers`, `scrubadub_spacy` | `regex` |
| `local_model_name` | Model name under `detectors/models/` (when `detector_type=local`); CLI: `-d --local-model NAME` | — |
| `labels` | List of labels (GLiNER / local) | built-in list |
| `threshold` | Global score threshold | `0.5` |
| `per_label_thresholds` | Label → threshold | `{}` |
| `regex_rules` | Label → `pattern` or `{ pattern: "..." }` | email, phone, iban, credit_card, ip |
| `gliner_model` | Model (detector_type=gliner): Hugging Face ID or path to local directory | `urchade/gliner_multi-v2.1` |
| `spacy_model` | SpaCy model (spacy / spacy_trf) | `en_core_web_sm` |
| `flair_model` | Flair model (flair) | `ner` |
| `transformers_model` | HuggingFace NER model (transformers) | `xlm-roberta-large-finetuned-conll03-english` |
| `presidio_language` | Presidio language (presidio) | `en` |
| `presidio_entities` | Presidio entity list; empty = default | `null` |
| `scrubadub_locale` | Scrubadub locale (scrubadub_spacy) | `en` |
| `tokenization.placeholder_format` | Format string, `{i}` = index | `[PII_{i}]` |
| `tokenization.immutable` | Placeholders are immutable | `true` |
| `tokenization.include_hash` | Add hash to mapping entries | `false` |
| `output.include_mapping` | Include mapping in outputs | `true` |

## Example

See `config.example.yml` in the repo root.
