"""
Basic flow: detect-encrypt then decrypt via the local API.

Run the API first:
  uvicorn private_layer.api.main:app --host 0.0.0.0 --port 9000

Then:
  python examples/basic_flow.py
"""
import os
import sys

# Add repo root so "private_layer" is importable when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import requests

API_URL = os.environ.get("PRIVATE_LAYER_URL", "http://localhost:9000")
API_KEY = os.environ.get("API_KEY", "dev-secret-demo")

def main():
    text = "Hi, I am John Doe. Email john.doe@example.com, phone +1 (415) 555-0199."
    r = requests.post(
        f"{API_URL}/v1/detect-encrypt",
        headers={"Content-Type": "application/json", "x-api-key": API_KEY},
        json={"tenant_id": "default", "text": text},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    print("Encrypted:", data["text_with_placeholders"])
    print("Bundles count:", len(data["bundles"]))

    r2 = requests.post(
        f"{API_URL}/v1/decrypt",
        headers={"Content-Type": "application/json", "x-api-key": API_KEY},
        json={
            "tenant_id": "default",
            "text_with_placeholders": data["text_with_placeholders"],
            "bundles": data["bundles"],
        },
        timeout=10,
    )
    r2.raise_for_status()
    print("Decrypted:", r2.json()["text"])
    assert r2.json()["text"] == text


if __name__ == "__main__":
    main()
