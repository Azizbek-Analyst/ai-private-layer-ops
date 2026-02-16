"""
Single source of truth for PII labels and label -> field mapping.
Used by config defaults and GLiNER (and optionally regex) for consistent field names.
"""

DEFAULT_LABELS = [
    "person name",
    "email address",
    "email",
    "phone number",
    "street address",
    "city",
    "postal code",
    "country",
    "national id number",
    "passport number",
    "driver license number",
    "insurance policy number",
    "credit card number",
    "ip address",
    "url",
]

LABEL2FIELD = {
    "person name": "person",
    "name": "person",
    "email address": "email",
    "email": "email",
    "phone number": "phone",
    "street address": "address",
    "city": "address",
    "postal code": "address",
    "country": "address",
    "national id number": "national_id",
    "passport number": "passport",
    "driver license number": "driver_license",
    "insurance policy number": "policy",
    "credit card number": "credit_card",
    "ip address": "ip",
    "url": "url",
}


# NER models (Presidio, SpaCy, Flair, etc.) often use uppercase tags
NER_LABEL_TO_FIELD = {
    "person": "person",
    "per": "person",
    "person_name": "person",
    "name": "person",
    "email": "email",
    "email_address": "email",
    "phone": "phone",
    "phone_number": "phone",
    "address": "address",
    "street_address": "address",
    "city": "address",
    "postal_code": "address",
    "country": "address",
    "location": "address",
    "geo": "address",
    "gpe": "address",
    "loc": "address",
    "national_id": "national_id",
    "passport": "passport",
    "driver_license": "driver_license",
    "policy": "policy",
    "credit_card": "credit_card",
    "ip": "ip",
    "ip_address": "ip",
    "url": "url",
}


def field_of(lbl: str) -> str:
    """Map detector label to canonical field name (supports both long labels and NER tags)."""
    s = lbl.strip().lower()
    if s in LABEL2FIELD:
        return LABEL2FIELD[s]
    n = s.replace(" ", "_").replace("-", "_")
    if n in NER_LABEL_TO_FIELD:
        return NER_LABEL_TO_FIELD[n]
    return s
