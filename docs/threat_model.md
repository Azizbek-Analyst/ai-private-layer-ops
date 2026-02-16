# Threat model (OSS v0.1)

## In scope

- **Local / dev use**: PII in text is replaced by placeholders; mapping is kept in memory or in files you control. No server; no automatic telemetry.
- **Mapping**: Contains original PII. User is responsible for securing the mapping (e.g. not logging, encrypting at rest if needed).

## Out of scope (v0.1)

- **Key management**: No KMS/HSM; optional encryption is demo-level.
- **Multi-tenant / auth**: No API keys, no tenant allowlists in OSS.
- **Guarantees on detector accuracy**: Regex and NER models can miss or over-detect; use for dev/tooling, not as sole control for compliance.

## Recommendations

- Do not log `mapping` or `original_text`.
- For production, integrate key management and encryption outside this library.
