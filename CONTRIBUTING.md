## Contributing to AI Private Layer (OPS)

Thank you for contributing to AI Private Layer.

This repository contains operational tooling and SDK components for privacy-preserving AI pipelines, including PII detection, masking, tokenization, and encryption utilities.

Because this project handles security-sensitive logic, we follow a **security-first** contribution model.

---

### 🧭 Contribution philosophy

We value:

- **Security by default**
- **Deterministic behavior**
- **Reproducibility**
- **Clear documentation**
- **Measurable detection performance**

We do **not** accept:

- Changes that expose plaintext PII in logs
- Weak or custom cryptography
- Breaking placeholder immutability guarantees
- Undocumented detection behavior

---

### 📌 Types of contributions

You may contribute:

- New PII detectors (regex / ML / NER)
- Performance improvements
- Bug fixes
- Test coverage expansion
- Documentation improvements
- Benchmark scripts
- CI/CD improvements

Large architectural changes should first be discussed via a GitHub issue with a short design proposal (scope, API impact, risks).

---

### 🛠 Development setup

Clone the repository:

```bash
git clone https://github.com/Azizbek-Analyst/ai-private-layer-ops.git
cd ai-private-layer-ops
```

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Lint (if configured in `pyproject.toml`):

```bash
ruff check .
black .
```

---

### 🧪 Testing requirements

All pull requests must:

- Include unit tests
- Not reduce overall coverage (within reason)
- Pass all CI checks
- Avoid leaking raw PII in test logs
- Include benchmark results if detection logic or cryptography is changed

If adding a new model or detector:

- Provide precision/recall/F1 evaluation
- Document dataset used
- Document supported languages
- Provide inference latency numbers (per 1k tokens / per request)

---

### 🔐 Cryptography rules

If your change affects encryption or key handling:

- Only use established libraries (e.g. `cryptography`)
- Do **not** implement custom crypto
- Do **not** downgrade encryption standards
- Maintain AES-GCM or stronger authenticated encryption

All crypto-related changes require explicit maintainer review.

For high-level expectations, see also `SECURITY.md`.

---

### 🏷 Placeholder integrity

Placeholders like:

```text
[PII_1]
[PII_2]
```

must remain:

- **Immutable**
- **Deterministic**
- **Non-overlapping**
- **Stable across mask/restore cycles**

Any change affecting token mapping must include round-trip tests:

```text
original → protect → restore == original
```

---

### 📤 Pull request process

1. Create a feature branch from `main`.
2. Implement changes with tests and docs.
3. Ensure all tests and linters pass.
4. Open a PR with a clear description and rationale.
5. Link related issues (if applicable).

Example PR titles:

- `feat(detector): add phone-number regex improvement`
- `fix(encryption): prevent IV reuse`
- `docs: improve config reference`

**PR checklist (recommended):**

- [ ] Tests added/updated
- [ ] No plaintext PII logging
- [ ] Docs updated (README / docs/*.md)
- [ ] Benchmarks attached (if detector/crypto changed)

---

### 🛡 Security review checklist

Before submitting:

- No plaintext PII logging
- No debug prints of sensitive data
- No secrets committed
- Mapping remains reversible
- Placeholders remain immutable and deterministic
- Encryption remains authenticated (AES-GCM or stronger)

For security disclosures, see `SECURITY.md`.

---

### 💬 Communication

Open an issue for:

- Design proposals
- Detector discussions
- Performance benchmarking debates
- Integration questions (pipelines, ETL, infra)

We encourage thoughtful, technically rigorous discussion.

For general questions and support, see `README.md` and `private-layer.ai`.

Thank you for helping build privacy-safe AI infrastructure.

