"""
AAD (Additional Authenticated Data) builder.
Format must match byte-for-byte between encrypt and decrypt.
"""
def build_aad(
    tenant: str,
    field: str,
    tok_id: str,
    schema: str,
    request_id: str,
) -> str:
    """
    Canonical AAD string. Order is critical; do not change.
    """
    return f"tenant={tenant}|field={field}|id={tok_id}|schema={schema}|req={request_id}"
