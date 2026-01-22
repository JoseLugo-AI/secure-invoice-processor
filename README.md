# 🛡️ Secure-Invoice-Enterprise: Surgical Redaction & Audit
**An AI-powered Financial Auditor with Automated PII Protection using Azure AI & GPT-4o.**

[![Status](https://img.shields.io/badge/Status-Production--Ready-success.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](#)
[![Security](https://img.shields.io/badge/Privacy-Surgical--Redaction-red.svg)](#)

## 📖 Overview
The **Secure-Invoice-Enterprise** is a specialized financial auditing tool designed for high-compliance environments. It solves the "Double-Bind" of AI auditing: needing to send data to a Large Language Model (LLM) while legally prohibited from sharing Personal Identifiable Information (PII). 

### Key Highlights:
* **✂️ Surgical Redaction:** Automatically detects and blacks out Customer PII (Names/Addresses) using Azure AI Document Intelligence coordinates before the data ever hits the LLM.
* **🕵️ Senior Auditor Persona:** Employs a hardened GPT-4o system prompt to validate VAT (Europe) and Sales Tax (USA) based on currency and address jurisdiction.
* **📅 Chronology Logic:** Built-in safeguards to detect future-dated invoices and verify tax periods against the current system date.
* **🔒 Data Sovereignty:** Leverages local image processing (PIL) to ensure that only "cleansed" images are transmitted to Azure OpenAI.

---

## ⚖️ Compliance & Governance Frameworks
Built to satisfy the requirements of international tax authorities and privacy regulators.

* **GDPR Article 32 (EU):** Implements "Privacy by Design" by redacting names and residential addresses of customers before cloud processing.
* **GoBD (Germany):** Supports the principles for the proper management and storage of books, records, and documents in electronic form.
* **US Sales Tax Nexus:** Logic determines if Sales Tax is applied correctly based on US-formatted addresses and currency.
* **NIST AI RMF:** Aligns with trustworthy AI standards by providing verifiable risk scores (0-100) for every document processed.

---

## 🛡️ Security & Hardening (CISSP Mindset)
This project focuses on the **Confidentiality** and **Integrity** of financial records:

* **Surgical Redaction:** Unlike standard "blurring," this engine uses pixel-perfect coordinate scaling to ensure zero PII leakage.
* **In-Memory Handshake:** Image buffers are cleared after processing to prevent data persistence in application memory.
* **Sanitized Export:** The Excel batch export uses a "Single Source of Truth" variable to ensure the risk score you see on screen is the one recorded in your audit logs.
* **VBS Launcher:** Includes a hidden background launcher to run the Streamlit engine as a secure service without an exposed terminal.

---

graph TD
    subgraph Local_Secure_Perimeter ["Local Environment (Secure)"]
        A[Invoices PDF/JPG] --> B[Surgical Redaction Engine]
        B --> C{PII Detected?}
        C -->|Yes| D[PIL/Pillow: Apply Blackout Polygons]
        C -->|No| E[Pass Through]
        D --> F[Sanitized Image Buffer]
        E --> F
    end

    subgraph Azure_Cloud ["Azure Cloud Services"]
        F --> G[Azure AI Document Intelligence]
        G --> H[Azure OpenAI: GPT-4o Audit]
    end

    subgraph Final_Audit_Output ["Final Audit Output"]
        H --> I[XlsxWriter: Excel Audit Log]
        H --> J[Redacted PDF/Image Export]
    end

    %% Styling
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#dfd,stroke:#333,stroke-width:4px
    style H fill:#ddf,stroke:#333,stroke-width:2px

---

## 🚀 Getting Started

### Prerequisites
- Python 3.14+
- Azure AI Document Intelligence (Prebuilt-Invoice Model)
- Azure OpenAI (GPT-4o deployment)
- [Poppler](https://poppler.freedesktop.org/) (Required for PDF rendering)

### Installation & Usage
1. **Clone the repo:**
   git clone https://github.com/JoseLugo-AI/secure-invoice-enterprise.git
   cd secure-invoice-enterprise

2. **Install dependencies:**
   pip install -r requirements.txt

3. **Configure Environment:** Create a .env file from the .env.example template and add your Azure credentials.

4. **Launch Application:**
   Run the run_secure_app.bat to launch the enterprise interface in standalone mode.

---

## 📜 License & Contributions
* **License:** MIT License.
* **Contributing:** Issues and Pull Requests are welcome for expanding tax jurisdiction logic or improving OCR accuracy.

---

## 👨‍💻 Author
**Jose Lugo** *Infrastructure Security Expert & AI Solutions Architect*

A 12-year **U.S. Army Veteran** and **Senior Systems Administrator** specializing in **Cybersecurity (CISSP/Security+)**. Based in Germany, I bridge the gap between complex US-based security frameworks and European data privacy laws.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/jose-lugo-cissp-327045308/)
