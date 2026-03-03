---
title: AI Private Layer OSS Demo
emoji: 🔐
colorFrom: purple
colorTo: indigo
sdk: gradio
python_version: "3.10"
app_file: app.py
pinned: false
---

# 🔐 AI Private Layer — OSS Demonstration

This Space demonstrates an open-source example of **AI Private Layer** — a privacy-preserving pipeline designed to enable secure and compliant AI interactions.

AI Private Layer detects, masks, and optionally encrypts sensitive information (PII) before passing text to AI models.  
This demo shows how the core OSS toolkit operates in a live interactive setting:

- 🚀 Detect personally identifiable information
- 🛡 Mask and tokenize sensitive parts of text
- 🔁 Restore original text after processing
- 📡 See real responses from an AI model with no exposed PII

**Why this matters:**  
AI systems usually require data to work, but regulated environments (e.g., finance, insurance, healthcare) **must prevent sensitive data exposure**.  
This demo illustrates how AI can be used *without leaking personal data*, making it safe for compliance-restricted scenarios.

Try entering any text with names, email, phone numbers, or identifiers — and see the masked output and restored text.

---

## 🧠 Key Concepts

- **PII Detection:** Identify sensitive spans in text
- **Tokenization:** Replace with immutable placeholders like `[PII_1]`
- **Secure Model Integration:** AI models never see raw sensitive information
- **Reversible:** Original text can be restored when needed

This demo is part of the **AI Private Layer OSS toolkit** — a blueprint for building privacy-first AI applications.

---

## 🖥 Local run

From the repository root:

```bash
cd examples/hf-space
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install gradio
pip install -e "../.."[crypto]

export TOKEN_KEY_HEX=$(openssl rand -hex 32)
python app.py
```

After starting Gradio you will see a link in the console (typically `http://127.0.0.1:7860`).

## 🧩 UI fields

- **Input text** – text where you want to detect and encrypt sensitive data.
- **Detector / model** – which detection backend to use:
  - `regex (UI demo)` – uses the simple regex rules and checkboxes in this demo only;
  - `ner`, `presidio`, `spacy`, `spacy_trf`, `flair`, `transformers`, `scrubadub_spacy` – core detectors from `ai-private-layer` (require corresponding extras);
  - `local::<model_name>` – local model under `src/private_layer/detectors/models/<model_name>/`.
- **Fields to use for placeholders** – checkboxes that control which canonical fields (`person`, `email`, `phone`, `credit_card`, etc.) will be replaced with placeholders.
- **Custom regular expression** – optional regex; all matches will be encrypted with label `custom`.

Result:

- **Masked text with placeholders** – original text where detected values are replaced with placeholders (`[PERSON_...]`, `[CREDIT_CARD_...]`, `[DOB_...]`, `[CUSTOM_...]`, etc.).
- **Decryption keys (bundles JSON)** – *bundles* structure required to restore the original text using `decrypt_placeholders` or the CLI command `private-layer decrypt`.

## 🚀 Using with Hugging Face Spaces

To deploy as a Hugging Face Space:

1. Create a separate repository with:
   - `app.py` (copied from this example),
   - `requirements.txt` (include `gradio` and `ai-private-layer[crypto]` from PyPI or GitHub).
2. Configure a secret `TOKEN_KEY_HEX` in the Space settings (64 hex chars, e.g. `openssl rand -hex 32`).
3. Choose **Gradio** as the Space type — the platform will automatically run `app.py`.


