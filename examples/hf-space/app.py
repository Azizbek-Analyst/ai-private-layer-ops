import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import gradio as gr

# For local development we keep the original repo layout:
#   <repo_root>/src/private_layer/...
# On Hugging Face Spaces the package is expected to be installed via pip,
# so the fallback to `src/` will simply not be used.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

try:
    # Prefer installed package (Hugging Face, pip install, etc.)
    from private_layer import detect
    from private_layer.core.types import Span
    from private_layer.pipeline import encrypt_spans
    from private_layer.pipeline.decrypt import decrypt_placeholders
    from private_layer.crypto.models import Bundle
    from private_layer.config import default_config
    from private_layer.config.labels import LABEL2FIELD, field_of
except ImportError:
    # Fallback for local development from this repo (src/)
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from private_layer import detect
    from private_layer.core.types import Span
    from private_layer.pipeline import encrypt_spans
    from private_layer.pipeline.decrypt import decrypt_placeholders
    from private_layer.crypto.models import Bundle
    from private_layer.config import default_config
    from private_layer.config.labels import LABEL2FIELD, field_of


FIELD_REGEXES: dict[str, re.Pattern[str]] = {
    # Simple example: capitalized words (person name)
    "person": re.compile(r"\b([A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ][a-zа-яё]+)*)\b"),
    # Email (simplified, same as in config.example.yml)
    "email": re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"),
    # Phone numbers (approximate, similar to config.example.yml)
    "phone": re.compile(
        r"(?<!\d)(?:\+\d{1,3}\s?)?(?:\(\d{2,4}\)\s?)?[\d\-\s]{6,15}(?!\d)"
    ),
    # Address (very rough heuristic: house number + words)
    "address": re.compile(r"\b\d{1,4}\s+\S+(?:\s+\S+){0,5}\b"),
    # National ID (rough heuristic: 6–12 digits)
    "national_id": re.compile(r"\b\d{6,12}\b"),
    # Passport (letters/digits, 5–15 chars)
    "passport": re.compile(r"\b[A-Z0-9]{5,15}\b", re.IGNORECASE),
    # Driver license (letters/digits/dashes, 5–20 chars)
    "driver_license": re.compile(r"\b[A-Z0-9\-]{5,20}\b", re.IGNORECASE),
    # Policy number (letters/digits/dashes, 5–30 chars)
    "policy": re.compile(r"\b[A-Z0-9\-]{5,30}\b", re.IGNORECASE),
    # Credit card: 13–19 digits, allow spaces/dashes
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    # IPv4 address
    "ip": re.compile(
        r"\b(?:(?:2(?:5[0-5]|[0-4]\d))|(?:1?\d?\d))(?:\.(?:2(?:5[0-5]|[0-4]\d)|1?\d?\d)){3}\b"
    ),
    # URL
    "url": re.compile(
        r"(?i)\bhttps?://[^\s/$.?#].[^\s]*\b"
    ),
    # Date of birth in YYYY-MM-DD format (example)
    "dob": re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
}

# List of available fields based on LABEL2FIELD (single source of truth)
FIELD_CHOICES = sorted(set(LABEL2FIELD.values()))


def available_local_models() -> List[str]:
    models_dir = ROOT / "src" / "private_layer" / "detectors" / "models"
    if not models_dir.exists():
        return []
    return sorted(
        [p.name for p in models_dir.iterdir() if p.is_dir()]
    )


LOCAL_MODELS = available_local_models()


def build_spans(
    text: str,
    selected_fields: Optional[List[str]],
    custom_regex: Optional[str],
) -> List[Span]:
    spans: List[Span] = []
    selected_fields = selected_fields or []

    for field in selected_fields:
        pattern = FIELD_REGEXES.get(field)
        if not pattern:
            continue
        for match in pattern.finditer(text):
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    label=field,
                    source="regex",
                )
            )

    if custom_regex:
        try:
            custom_pattern = re.compile(custom_regex)
        except re.error as exc:
            raise gr.Error(f"Invalid regular expression: {exc}") from exc
        for match in custom_pattern.finditer(text):
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    label="custom",
                    source="regex",
                )
            )

    if not spans:
        return []

    # Простейшее разрешение пересечений: оставляем более длинные/ранние спаны
    spans_sorted = sorted(spans, key=lambda s: (s.start, -(s.end - s.start)))
    resolved: List[Span] = []
    last_end = -1
    for span in spans_sorted:
        if span.start >= last_end:
            resolved.append(span)
            last_end = span.end
    return resolved


def encrypt_text(
    text: str,
    fields: Optional[List[str]],
    custom_regex: str,
    backend: str,
    model_name: str,
    token_key_override: str,
) -> tuple[str, str]:
    text = (text or "").strip()
    if not text:
        raise gr.Error("Please provide text to encrypt.")

    # Determine spans either via UI regex or via one of the supported detectors
    spans: List[Span]
    model_name = (model_name or "").strip()

    if backend == "regex (UI demo)":
        spans = build_spans(text, fields, custom_regex or None)
    elif backend.startswith("local::"):
        model_name = backend.split("::", 1)[1].strip()
        if not model_name:
            return text, "Error: detector model is not selected."
        cfg = default_config()
        cfg.detector_type = "local"
        cfg.local_model_name = model_name
        try:
            det_result = detect(text, config=cfg)
        except Exception as exc:
            return (
                text,
                "Error running local model.\n\n"
                f"Model: {model_name}\n"
                f"Details: {exc}\n\n"
                "Make sure the local model is available under `detectors/models/` "
                "and extras `[local_model]` are installed.",
            )
        spans = [
            Span(
                start=s.start,
                end=s.end,
                label=field_of(s.label),
                score=s.score,
                source=s.source or "model",
            )
            for s in det_result.spans
        ]
    else:
        # Other detectors: presidio, spacy, flair, transformers, scrubadub_spacy, ner, etc.
        det_type = backend.strip()
        cfg = default_config()
        cfg.detector_type = det_type
        # For transformers allow overriding model name from UI
        if det_type == "transformers" and model_name:
            cfg.transformers_model = model_name
        try:
            det_result = detect(text, config=cfg)
        except Exception as exc:
            return (
                text,
                "Error running detector.\n\n"
                f"Detector: {det_type}\n"
                f"Details: {exc}\n\n"
                "Make sure the corresponding extras are installed "
                "(e.g. `.[flair]`, `.[presidio]`, `.[spacy]`, `.[transformers_ner]`, "
                "`.[scrubadub]`) and models are configured.\n",
            )
        spans = [
            Span(
                start=s.start,
                end=s.end,
                label=field_of(s.label),
                score=s.score,
                source=s.source or det_type,
            )
            for s in det_result.spans
        ]
    if not spans:
        return text, "No matches found for encryption."

    token_key_hex = (token_key_override or "").strip()
    if not token_key_hex:
        token_key_hex = os.environ.get("TOKEN_KEY_HEX", "").strip()

    if not token_key_hex:
        return text, (
            "Error: TOKEN_KEY_HEX is not set.\n\n"
            "You can either:\n"
            "- paste a 64-char hex key into the TOKEN_KEY_HEX field below, or\n"
            "- set TOKEN_KEY_HEX as an environment variable (e.g. in HF Space secrets).\n"
        )

    if len(token_key_hex) != 64:
        return text, (
            "Error: TOKEN_KEY_HEX must be exactly 64 hex characters.\n"
            "Example: openssl rand -hex 32\n"
        )

    try:
        token_key = bytes.fromhex(token_key_hex)
    except ValueError:
        return text, (
            "Error: TOKEN_KEY_HEX is not valid hex.\n"
            "It must contain only [0-9a-f].\n"
        )

    masked_text, bundles = encrypt_spans(
        text,
        spans,
        token_key=token_key,
        tenant_id="hf-space",
        schema="v1",
        salt=None,
    )

    bundles_json = json.dumps(
        [b.to_dict() for b in bundles],
        ensure_ascii=False,
        indent=2,
    )

    return masked_text, bundles_json


def decrypt_text(masked_text: str, bundles_json: str, salt: str | None) -> str:
    masked_text = (masked_text or "").strip()
    if not masked_text:
        return (
            "Error: please provide text with placeholders to decrypt.\n"
            "The “Masked text” field must not be empty."
        )

    try:
        raw = json.loads(bundles_json or "[]")
    except json.JSONDecodeError as exc:
        return (
            "Error: invalid JSON in the “Bundles JSON” field.\n"
            f"Details: {exc}\n\n"
            "Make sure you copied the bundles completely and without modification."
        )

    if not isinstance(raw, list):
        return (
            "Error: expected a JSON array of bundles (list of objects).\n"
            "Example: [ {\"id\": \"...\", \"wrapped_dek\": \"...\", ... }, ... ]"
        )

    bundles: List[Bundle] = [
        Bundle.from_dict(b) if isinstance(b, dict) else b for b in raw
    ]

    try:
        restored = decrypt_placeholders(masked_text, bundles, salt=salt or None)
    except Exception:
        return (
            "Error: failed to decrypt data.\n\n"
            "Please check that:\n"
            "- the masked text matches the provided bundles;\n"
            "- the bundles JSON was copied fully and not modified;\n"
            "- the same TOKEN_KEY_HEX (and salt, if used) is configured.\n"
        )

    return restored


def load_example() -> tuple[str, List[str], str]:
    text = (
        "Hi, my name is John Doe, you can reach me at john.doe@example.com "
        "or +1 (415) 555-0130. I live at 123 Market Street, San Francisco."
    )
    default_fields = [
        f
        for f in FIELD_CHOICES
        if f in {"person", "email", "phone", "address"}
    ]
    return text, default_fields, ""


def generate_token_key() -> str:
    return os.urandom(32).hex()


with gr.Blocks(title="AI Private Layer — encrypt / decrypt PII") as demo:
    gr.Markdown(
        """
        ## 🔐 AI Private Layer — OSS Demonstration

        This Space demonstrates an open-source example of **AI Private Layer** — a privacy-preserving pipeline
        designed to enable secure and compliant AI interactions.

        AI Private Layer detects, masks, and optionally encrypts sensitive information (PII) before passing text to AI models.  
        This demo shows how the core OSS toolkit operates in a live interactive setting:

        - 🚀 Detect personally identifiable information  
        - 🛡 Mask and tokenize sensitive parts of text  
        - 🔁 Restore original text after processing  
        - 📡 Keep AI models from ever seeing raw PII

        **Why this matters:**  
        AI systems usually require data to work, but regulated environments (e.g., finance, insurance, healthcare)
        **must prevent sensitive data exposure**.  
        This demo illustrates how AI can be used *without leaking personal data*, making it safe for compliance‑restricted scenarios.

        Try entering any text with names, email, phone numbers, or identifiers — and see the masked output and restored text.
        """
    )

    with gr.Tab("Encryption"):
        with gr.Row():
            with gr.Column(scale=2):
                input_text = gr.Textbox(
                    label="Input text",
                    placeholder="Paste text containing PII...",
                    lines=8,
                )
                token_key_box = gr.Textbox(
                    label="TOKEN_KEY_HEX (optional override)",
                    placeholder="Paste or generate a 64-char hex key",
                    lines=1,
                    type="text",
                )
                generate_token_button = gr.Button(
                    "Generate TOKEN_KEY_HEX (non-persistent demo key)",
                    variant="secondary",
                )
                backend_choices: List[str] = ["regex (UI demo)"]
                # Supported detectors from the core library
                backend_choices += [
                    "ner",
                    "presidio",
                    "spacy",
                    "spacy_trf",
                    "flair",
                    "transformers",
                    "scrubadub_spacy",
                ]
                # Local models (gliner / local_model_detector)
                if LOCAL_MODELS:
                    backend_choices += [f"local::{name}" for name in LOCAL_MODELS]
                backend_dropdown = gr.Dropdown(
                    label="Detector / model",
                    choices=backend_choices,
                    value=backend_choices[0],
                )
                backend_model_name = gr.Textbox(
                    label="Model name (for transformers etc., optional)",
                    placeholder="E.g. xlm-roberta-large-finetuned-conll03-english",
                    lines=1,
                )
                field_choices = gr.CheckboxGroup(
                    label="Fields to use for placeholders (from labels.py)",
                    choices=FIELD_CHOICES,
                    value=[
                        f
                        for f in FIELD_CHOICES
                        if f
                        in {
                            "person",
                            "email",
                            "phone",
                            "address",
                            "credit_card",
                            "ip",
                            "url",
                        }
                    ],
                )
                custom_regex_box = gr.Textbox(
                    label="Custom regular expression (optional)",
                    placeholder=r"E.g. \\b\\d{10}\\b",
                    lines=2,
                )
                with gr.Row():
                    example_button = gr.Button("Example", variant="secondary")
                    encrypt_button = gr.Button("Encrypt", variant="primary")

            with gr.Column(scale=2):
                masked_output = gr.Textbox(
                    label="Masked text with placeholders",
                    lines=8,
                )
                bundles_output = gr.Textbox(
                    label="Decryption keys (bundles JSON)",
                    lines=12,
                )

        example_button.click(
            fn=load_example,
            inputs=None,
            outputs=[input_text, field_choices, custom_regex_box],
        )

        generate_token_button.click(
            fn=generate_token_key,
            inputs=None,
            outputs=[token_key_box],
        )

        encrypt_button.click(
            fn=encrypt_text,
            inputs=[
                input_text,
                field_choices,
                custom_regex_box,
                backend_dropdown,
                backend_model_name,
                token_key_box,
            ],
            outputs=[masked_output, bundles_output],
        )

    with gr.Tab("Decryption"):
        with gr.Row():
            with gr.Column(scale=2):
                dec_masked_input = gr.Textbox(
                    label="Masked text",
                    placeholder="Paste masked_text returned from encryption...",
                    lines=8,
                )
                dec_bundles_input = gr.Textbox(
                    label="Bundles JSON",
                    placeholder="Paste JSON with bundles (from the field above or a file)...",
                    lines=12,
                )
                dec_salt = gr.Textbox(
                    label="Salt (optional)",
                    placeholder="Usually can be left empty if salt is stored in bundles",
                    lines=1,
                )
                decrypt_button = gr.Button("Decrypt", variant="primary")

            with gr.Column(scale=2):
                dec_output = gr.Textbox(
                    label="Restored text",
                    lines=12,
                )

        decrypt_button.click(
            fn=decrypt_text,
            inputs=[dec_masked_input, dec_bundles_input, dec_salt],
            outputs=[dec_output],
        )


if __name__ == "__main__":
    demo.launch()

