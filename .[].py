#!/usr/bin/env python3
"""
Entry point: CLI or demo.

Usage:
  python run.py                    — invoke CLI (private-layer --help)
  python run.py protect "text"     — same as private-layer protect "text"
  python run.py demo               — short demo: protect + restore (no encryption)
  python run.py demo --crypto      — demo with encryption (requires pip install -e ".[crypto]")
"""
import os
import sys

# Add src to path when package is not installed
_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo(crypto="--crypto" in sys.argv)
        return
    # Otherwise pass all arguments to CLI
    from private_layer.cli.app import main as cli_main
    cli_main()


def run_demo(use_crypto: bool = False):
    if use_crypto:
        _run_demo_crypto()
    else:
        _run_demo_plain()


def _run_demo_plain():
    from private_layer import protect, restore
    text = "Email me at john@example.com or call +1 555 123 4567."
    print("Original text:", text)
    r = protect(text)
    print("After protect:", r.masked_text)
    restored = restore(r.masked_text, r.mapping)
    print("After restore:", restored)
    assert restored == text
    print("OK (roundtrip without encryption)")


def _run_demo_crypto():
    try:
        from private_layer.core.types import Span
        from private_layer.pipeline.encrypt import encrypt_spans
        from private_layer.pipeline.decrypt import decrypt_placeholders
    except ImportError as e:
        print("For encryption demo install: pip install -e \".[crypto]\"")
        raise SystemExit(1) from e
    token_key = os.urandom(32)
    text = "Secret: alice@secret.com"
    spans = [Span(8, 23, "email", None, "regex")]
    masked, bundles = encrypt_spans(
        text, spans, token_key=token_key, tenant_id="demo", schema="v1", salt="demo-salt"
    )
    print("Original text:", text)
    print("Encrypted (placeholders):", masked)
    restored = decrypt_placeholders(masked, bundles, salt="demo-salt")
    print("Decrypted:", restored)
    assert restored == text
    print("OK (roundtrip with AES-GCM)")


if __name__ == "__main__":
    main()
