"""Typer CLI entrypoint."""
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Optional

import typer

from private_layer import detect, protect, restore
from private_layer.config import Config, default_config, load_config
from private_layer.core.types import MappingEntry
from private_layer.io import stream_protect

app = typer.Typer(
    name="private-layer",
    help="AI Private Layer — PII detection and tokenization (SDK + CLI).",
)


def _get_config(config_path: Optional[Path]) -> Config:
    if config_path and config_path.exists():
        return load_config(config_path)
    return default_config()


def _config_with_detector_options(
    base: Config,
    use_local: bool = False,
    detector: Optional[str] = None,
    local_model: Optional[str] = None,
    presidio_language: Optional[str] = None,
    presidio_entities: Optional[str] = None,
) -> Config:
    """Apply CLI detector overrides. -d + --local-model => detector_type=local, model from detectors/models/."""
    cfg = base
    if use_local and local_model:
        cfg = replace(
            cfg,
            detector_type="local",
            local_model_name=local_model.strip(),
        )
    elif detector is not None:
        cfg = replace(cfg, detector_type=detector.strip().lower())
        if local_model is not None:
            path = local_model.strip()
            t = cfg.detector_type
            if t in ("gliner", "ner"):
                cfg = replace(cfg, gliner_model=path)
            elif t in ("spacy", "spacy_trf"):
                cfg = replace(cfg, spacy_model=path)
            elif t == "flair":
                cfg = replace(cfg, flair_model=path)
            elif t == "transformers":
                cfg = replace(cfg, transformers_model=path)
    if presidio_language is not None:
        cfg = replace(cfg, presidio_language=presidio_language.strip())
    if presidio_entities is not None:
        entities = [e.strip() for e in presidio_entities.split(",") if e.strip()]
        cfg = replace(cfg, presidio_entities=entities if entities else None)
    return cfg


@app.command("detect")
def detect_cmd(
    text: str = typer.Argument(..., help="Input text"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", path_type=Path),
    use_local: bool = typer.Option(False, "-d", "--use-local", help="Use local model from detectors/models/; requires --local-model"),
    detector: Optional[str] = typer.Option(
        None, "--detector", "-p",
        help="Detector type: regex, presidio, ner, spacy, spacy_trf, flair, transformers, scrubadub_spacy",
    ),
    local_model: Optional[str] = typer.Option(None, "--local-model", "-m", help="Local model name (e.g. private-layer-v1); use with -d"),
    presidio_language: Optional[str] = typer.Option(None, "--presidio-language", help="Presidio language (e.g. en)"),
    presidio_entities: Optional[str] = typer.Option(None, "--presidio-entities", help="Presidio entities, comma-separated (default: all)"),
    format: str = typer.Option("json", "--format", "-f", help="Output: json | text"),
) -> None:
    """Detect PII spans in text."""
    if use_local and not local_model:
        typer.echo("When using -d (local model), provide --local-model NAME (e.g. -d --local-model private-layer-v1)", err=True)
        raise typer.Exit(1)
    cfg = _get_config(config)
    cfg = _config_with_detector_options(
        cfg,
        use_local=use_local,
        detector=detector,
        local_model=local_model,
        presidio_language=presidio_language,
        presidio_entities=presidio_entities,
    )
    result = detect(text, config=cfg)
    if format == "text":
        for s in result.spans:
            typer.echo(f"{s.start}:{s.end} {s.label} {repr(text[s.start:s.end])}")
    else:
        out = {
            "spans": [
                {"start": s.start, "end": s.end, "label": s.label}
                for s in result.spans
            ]
        }
        typer.echo(json.dumps(out, indent=2))


@app.command("protect")
def protect_cmd(
    text: str = typer.Argument(..., help="Input text"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", path_type=Path),
    use_local: bool = typer.Option(False, "-d", "--use-local", help="Use local model from detectors/models/; requires --local-model"),
    detector: Optional[str] = typer.Option(
        None, "--detector", "-p",
        help="Detector type: regex, presidio, ner, spacy, spacy_trf, flair, transformers, scrubadub_spacy",
    ),
    local_model: Optional[str] = typer.Option(None, "--local-model", "-m", help="Local model name (e.g. private-layer-v1); use with -d"),
    presidio_language: Optional[str] = typer.Option(None, "--presidio-language", help="Presidio language (e.g. en)"),
    presidio_entities: Optional[str] = typer.Option(None, "--presidio-entities", help="Presidio entities, comma-separated (default: all)"),
    format: str = typer.Option("json", "--format", "-f", help="Output: json | text"),
    include_mapping: bool = typer.Option(True, "--include-mapping/--no-include-mapping"),
    encrypt: bool = typer.Option(
        False, "--encrypt", "-e",
        help="Use AES-GCM encryption; output bundles for later decrypt (requires TOKEN_KEY_HEX, pip install -e '.[crypto]')",
    ),
    tenant_id: str = typer.Option("default", "--tenant", "-t", help="Tenant id (for encrypt mode)"),
    salt: Optional[str] = typer.Option(None, "--salt", "-s", help="Optional salt (for encrypt mode)"),
) -> None:
    """Replace PII with placeholders; output masked text and mapping (or encrypted bundles with --encrypt)."""
    if use_local and not local_model:
        typer.echo("When using -d (local model), provide --local-model NAME (e.g. -d --local-model private-layer-v1)", err=True)
        raise typer.Exit(1)
    cfg = _get_config(config)
    cfg = _config_with_detector_options(
        cfg,
        use_local=use_local,
        detector=detector,
        local_model=local_model,
        presidio_language=presidio_language,
        presidio_entities=presidio_entities,
    )
    if encrypt:
        _protect_encrypt(text, config=cfg, tenant_id=tenant_id, salt=salt, format=format)
        return
    result = protect(text, config=cfg)
    if format == "text":
        typer.echo(result.masked_text)
        if include_mapping:
            for e in result.mapping:
                typer.echo(f"  {e.placeholder} -> {e.label}: {repr(e.original_text)}")
    else:
        out = {"masked_text": result.masked_text}
        if include_mapping:
            out["mapping"] = [e.to_dict() for e in result.mapping]
        typer.echo(json.dumps(out, indent=2, ensure_ascii=False))


def _protect_encrypt(
    text: str,
    config: Config,
    tenant_id: str,
    salt: Optional[str],
    format: str,
) -> None:
    try:
        from private_layer.pipeline.encrypt import encrypt_spans
    except ImportError:
        typer.echo(
            "Encryption requires: pip install -e \".[crypto]\"",
            err=True,
        )
        raise typer.Exit(1)
    token_key_hex = os.environ.get("TOKEN_KEY_HEX")
    if not token_key_hex or len(token_key_hex) != 64:
        typer.echo(
            "With --encrypt set TOKEN_KEY_HEX (64 hex chars). Example: openssl rand -hex 32",
            err=True,
        )
        raise typer.Exit(1)
    token_key = bytes.fromhex(token_key_hex)
    det = detect(text, config=config)
    if not det.spans:
        out = {"masked_text": text, "bundles": []}
        typer.echo(json.dumps(out, indent=2, ensure_ascii=False))
        return
    masked, bundles = encrypt_spans(
        text,
        det.spans,
        token_key=token_key,
        tenant_id=tenant_id,
        schema="v1",
        salt=salt,
    )
    # With --encrypt always output JSON (masked_text + bundles) for consistent decrypt usage
    out = {
        "masked_text": masked,
        "bundles": [b.to_dict() for b in bundles],
    }
    typer.echo(json.dumps(out, indent=2, ensure_ascii=False))


@app.command("restore")
def restore_cmd(
    masked_text: str = typer.Argument(..., help="Masked text with placeholders"),
    mapping: str = typer.Argument(..., help="JSON array of mapping entries"),
) -> None:
    """Restore original text from masked text and mapping JSON (tokenization only)."""
    mapping_list = json.loads(mapping)
    entries = [
        MappingEntry.from_dict(e) if isinstance(e, dict) else e for e in mapping_list
    ]
    out = restore(masked_text, entries)
    typer.echo(out)


@app.command("decrypt")
def decrypt_cmd(
    masked_text: str = typer.Argument(..., help="Masked text with encrypted placeholders [FIELD_id]"),
    bundles: str = typer.Argument(..., help="JSON array of bundles (output of protect --encrypt)"),
    salt: Optional[str] = typer.Option(None, "--salt", "-s", help="Salt if not stored in bundles"),
) -> None:
    """Decrypt and restore text using bundles (from protect --encrypt)."""
    try:
        from private_layer.pipeline.decrypt import decrypt_placeholders
        from private_layer.crypto.models import Bundle
    except ImportError:
        typer.echo("Decryption requires: pip install -e \".[crypto]\"", err=True)
        raise typer.Exit(1)
    raw = json.loads(bundles)
    bundle_list = [Bundle.from_dict(b) if isinstance(b, dict) else b for b in raw]
    out = decrypt_placeholders(masked_text, bundle_list, salt=salt)
    typer.echo(out)


dataset_app = typer.Typer(help="Dataset (JSONL) commands.")
app.add_typer(dataset_app, name="dataset")


@dataset_app.command("protect")
def dataset_protect(
    input: Path = typer.Option(..., "--input", "-i", path_type=Path),
    output: Path = typer.Option(..., "--output", "-o", path_type=Path),
    text_field: str = typer.Option("text", "--text-field"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", path_type=Path),
    use_local: bool = typer.Option(False, "-d", "--use-local", help="Use local model from detectors/models/; requires --local-model"),
    detector: Optional[str] = typer.Option(None, "--detector", "-p", help="Detector type (e.g. presidio, ner, spacy, flair, transformers, scrubadub_spacy)"),
    local_model: Optional[str] = typer.Option(None, "--local-model", "-m", help="Local model name (e.g. private-layer-v1); use with -d"),
    presidio_language: Optional[str] = typer.Option(None, "--presidio-language"),
    presidio_entities: Optional[str] = typer.Option(None, "--presidio-entities"),
    include_mapping: bool = typer.Option(False, "--include-mapping/--no-include-mapping"),
) -> None:
    """Stream JSONL: protect text field line-by-line."""
    cfg = _get_config(config)
    if use_local and not local_model:
        typer.echo("When using -d (local model), provide --local-model NAME (e.g. -d --local-model private-layer-v1)", err=True)
        raise typer.Exit(1)
    cfg = _config_with_detector_options(
        cfg,
        use_local=use_local,
        detector=detector,
        local_model=local_model,
        presidio_language=presidio_language,
        presidio_entities=presidio_entities,
    )
    n = stream_protect(
        input_path=input,
        output_path=output,
        text_field=text_field,
        config=cfg,
        include_mapping=include_mapping,
    )
    typer.echo(f"Processed {n} lines -> {output}", err=True)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
