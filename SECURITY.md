## Security Policy

AI Private Layer handles sensitive data and cryptographic operations.

Security is our highest priority.

---

### 🚨 Reporting a vulnerability

**Do not** open a public GitHub issue for security vulnerabilities.

Instead, report responsibly via:

- **Email**: `support@private-layer.ai`

Please include:

- Description of the issue
- Steps to reproduce (if possible)
- Potential impact
- Suggested mitigation (if known)

We aim to acknowledge reports within **72 hours**.

---

### 🔐 Security model

AI Private Layer follows these principles:

1. **Zero-trust assumption** (treat all inputs as untrusted)
2. **No plaintext PII persistence** (mappings are sensitive, logs must not contain PII)
3. **Immutable placeholders** (e.g. `[PII_1]`, `[PII_2]`)
4. **Authenticated encryption** (AES-GCM or stronger)
5. **Deterministic, reversible mapping**
6. **No secret storage in code or VCS**

See `docs/architecture.md` for a high-level overview of the pipeline.

---

### 🔑 Cryptography

Current expectations:

- AES-GCM (256-bit) for authenticated encryption
- Secure random IV/nonce generation
- Keys provided via environment variables (e.g. `TOKEN_KEY_HEX`)
- No home-grown crypto or custom primitives

We do **not** accept:

- ECB mode
- Weak or deprecated hashes
- Static or predictable IVs
- Custom cryptographic algorithms or protocols

Any change affecting cryptography must be:

- Implemented using well-vetted libraries (e.g. `cryptography`)
- Reviewed by a maintainer with security context
- Covered by tests and, where applicable, benchmarks

---

### 📦 Dependency security

We:

- Monitor CVEs for critical dependencies where feasible
- Update dependencies regularly
- Recommend pinned versions via `pyproject.toml`
- Encourage use of security scanning tools (SCA, SAST) in CI

If you notice a vulnerable dependency, please open an issue or contact us via email.

---

### 🔁 Supported versions

| Version | Supported |
|--------:|:---------|
| 1.x     | Yes      |
| <1.0    | No       |

For current releases and changelog, see the project page on GitHub and `pyproject.toml`.

---

### 🛡 Hardening recommendations

For production deployments of AI Private Layer:

- Store encryption keys in a secure vault (HSM, KMS, or secret manager)
- Rotate encryption keys regularly
- Enable structured logging **without** PII
- Run static security analysis on your codebase
- Enable container and image scanning if you containerize
- Isolate the detection/tokenization layer from external model calls where possible
- Restrict network egress where local-only processing is required

---

### 🏆 Responsible disclosure

We appreciate ethical security research.

- Please follow the reporting process above.
- Do not exploit vulnerabilities beyond what is necessary to demonstrate impact.
- Do not access, modify, or destroy data that you do not own.

With your consent, we may credit you in release notes or `SECURITY.md` for responsibly reported vulnerabilities.

For more information about the project and its ecosystem, see `README.md` and `https://private-layer.ai`.

