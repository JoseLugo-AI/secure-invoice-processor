import os
import io
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

# Third-party libraries
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from openai import AzureOpenAI
from pdf2image import convert_from_bytes # Make sure to pip install pdf2image pillow

load_dotenv()

# 1. Initialize Document Intelligence (The "Eyes")
doc_client = DocumentIntelligenceClient(
    endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
)

# 2. Initialize Azure OpenAI (The "Brain")
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_retries=3,
    timeout=60.0 
)

def extract_invoice_data(file_bytes):
    """PHASE 1: Extract structured data using Document Intelligence"""
    poller = doc_client.begin_analyze_document(
        model_id="prebuilt-invoice", 
        body=file_bytes
    )
    result = poller.result()
    
    data = {"vendor": "Unknown", "total": "0.00", "tax": "0.00", "date": "N/A", "items": []}
    
    if result.documents:
        doc = result.documents[0]
        fields = doc.fields
        
        # Clean up strings to remove the \n that confused the AI
        data["vendor"] = fields.get("VendorName", {}).get("content", "N/A").replace('\n', ' ').strip()
        data["total"] = fields.get("InvoiceTotal", {}).get("content", "0.00").replace('\n', ' ').strip()
        data["date"] = fields.get("InvoiceDate", {}).get("content", "N/A")
        data["tax"] = fields.get("TotalTax", {}).get("content", "0.00").replace('\n', ' ').strip()
        
        if "Items" in fields:
            for item in fields["Items"].get("valueArray", []):
                item_obj = item.get("valueObject", {})
                data["items"].append({
                    "description": item_obj.get("Description", {}).get("content", "N/A").replace('\n', ' '),
                    "amount": item_obj.get("Amount", {}).get("content", 0)
                })
    return data

def security_audit(file_bytes, extracted_data, is_pdf=False):
    """PHASE 2: Global Audit (Fixed & Dynamically Future-Proofed)"""
    try:
        # 1. Convert PDF to Image if necessary
        if is_pdf:
            poppler_bin = os.path.normpath(os.getenv("POPPLER_PATH"))
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1, poppler_path=poppler_bin)
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='JPEG')
            final_bytes = img_byte_arr.getvalue()
        else:
            final_bytes = file_bytes

        # 2. Define the base64_image variable
        base64_image = base64.b64encode(final_bytes).decode('utf-8')
        
        # 3. Get current date details dynamically
        now = datetime.now()
        today_str = now.strftime("%d.%m.%Y")
        current_year = now.year 

        response = openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=[
                {
                    "role": "system", 
                    "content": (
                        f"Today's date is {today_str}. The current year is {current_year}. "
                        "You are a Senior International Tax Auditor. Apply these combined rules:\n\n"
                        "1. CHRONOLOGY: Compare all dates to the system date. "
                        f"Years 2024 and 2025 are smaller than {current_year}, therefore they are PAST dates. "
                        "NEVER flag 2024 or 2025 as 'Future'. Only year > 2026 is future.\n"
                        "2. JURISDICTION: Determine country (US/UK/EU) via Currency, Address, and VAT ID. "
                        "Apply local date formats (EU/UK: DD.MM.YYYY | US: MM/DD/YYYY).\n"
                        "3. TAX AUDIT: Validate VAT (Europe) or Sales Tax (USA) based on the identified country. "
                        "Ensure (Net + Tax + Shipping = Gross Total).\n"
                        "4. FINAL ASSESSMENT: You MUST end your report with exactly one line: "
                        "'RISK_SCORE: X' (where X is 0-100). 0 is safe, 100 is fraud."
                    )
                },
                {"role": "user", "content": [
                    {"type": "text", "text": f"Audit this data: {json.dumps(extracted_data)}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # This will now catch and print the specific error in the terminal
        print(f"Audit Error: {e}")
        return f"Audit failed: {e}"