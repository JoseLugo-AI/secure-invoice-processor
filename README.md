# Secure Invoice Processor: Surgical Redaction & Audit
**Portfolio demo — Azure AI invoice audit with automated PII redaction and GPT-4o.**

[![Status](https://img.shields.io/badge/Status-Portfolio--Demo-lightgrey.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](#)
[![Security](https://img.shields.io/badge/Privacy-Surgical--Redaction-red.svg)](#)

> **This is a portfolio / demo artifact, not a production product and not a client deployment.** It shows how I approach the "double-bind" of sending documents to an LLM while keeping personal data off the wire. My core offer is Microsoft 365 Copilot GDPR consulting: **[joselugo.de](https://joselugo.de)**.

## Overview
**Secure Invoice Processor** (this GitHub repo; older notes called it "Secure-Invoice-Enterprise") is a demo financial-audit workflow. It redacts customer PII locally, then asks GPT-4o to check VAT (Europe) and sales tax (USA) from what remains.

### Key Highlights
* **Surgical Redaction:** Detects and blacks out customer PII (names/addresses) using Azure AI Document Intelligence coordinates before the image hits the LLM.
* **Senior Auditor Persona:** A GPT-4o system prompt validates VAT (Europe) and sales tax (USA) from currency and address jurisdiction.
* **Chronology Logic:** Flags future-dated invoices and checks tax periods against the system date.
* **Data Sovereignty:** Local image processing (PIL) so only cleansed images are sent to Azure OpenAI.

![Architecture diagram](./Secure-Invoice-Enterprise%20Surgical%20Redaction%20%26%20Audit%20Diagram.png)

## Compliance & Governance Frameworks
This demo is built around the following themes (not an audit opinion or a certification):

* **GDPR Article 32 (EU):** Privacy by Design — names and residential addresses are redacted before cloud processing.
* **GoBD (Germany):** Touches principles for proper electronic books and records.
* **US Sales Tax Nexus:** Logic checks whether sales tax fits a US-formatted address and currency.
* **NIST AI RMF:** Each document gets a verifiable risk score (0–100).

## Security & Hardening (CISSP Mindset)
Focus is **confidentiality** and **integrity** of the demo audit path:

* **Surgical Redaction:** Coordinate scaling rather than blur, so redacted pixels stay unreadable.
* **In-Memory Handshake:** Image buffers are cleared after processing.
* **Sanitized Export:** Excel batch export uses a single source of truth for the on-screen risk score vs. the audit log.
* **VBS Launcher:** Optional hidden launcher to start Streamlit without an exposed terminal (Windows).

## Getting Started

### Prerequisites
- Python 3.14+
- Azure AI Document Intelligence (Prebuilt-Invoice model)
- Azure OpenAI (GPT-4o deployment)
- [Poppler](https://poppler.freedesktop.org/) (PDF rendering)

### Installation & Usage
1. **Clone the repo:**

   ```bash
   git clone https://github.com/JoseLugo-AI/secure-invoice-processor.git
   cd secure-invoice-processor
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:** Copy `.env.example` to `.env` and add your Azure credentials.

4. **Launch (Windows):** Run `run_secure_app.bat` for the standalone Streamlit UI.

   Or: `streamlit run app.py`

## License & Contributions
* **License:** MIT License.
* **Contributing:** Issues and pull requests welcome for tax-jurisdiction logic or OCR accuracy.

## Author
**Jose Lugo** — Infrastructure Security Expert & AI Solutions Architect

A 12-year **U.S. Army Veteran** and **Senior Systems Administrator** specializing in **Cybersecurity (CISSP/Security+)**. Based in Germany. Core consulting offer: Microsoft 365 Copilot GDPR / DSGVO — [joselugo.de](https://joselugo.de).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/jose-lugo-cissp-327045308/)