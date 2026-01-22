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
from pdf2image import convert_from_bytes 
from PIL import Image, ImageDraw

load_dotenv()

# 1. Initialize Clients
doc_client = DocumentIntelligenceClient(
    endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
)

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    max_retries=3,
    timeout=60.0 
)

# 2. Setup Secure Storage
REDACTED_DIR = "redacted_outputs"
if not os.path.exists(REDACTED_DIR):
    os.makedirs(REDACTED_DIR)

## SECURITY LAYER: REDACTION ENGINE ##
def apply_redaction(img_obj, polygons):
    """Draws black boxes on a PIL Image object using scaled coordinates."""
    print(f">>> ENGINE: Redacting {len(polygons)} areas...")
    try:
        img = img_obj.convert("RGB")
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size
        
        for poly in polygons:
            # Scale coordinates: Azure 0-1000 scale -> Actual Image Pixels
            points = []
            for i in range(0, 8, 2):
                x = (poly[i] / 1000) * img_w
                y = (poly[i+1] / 1000) * img_h
                points.append((x, y))
            draw.polygon(points, fill="black", outline="black")
        
        return img
    except Exception as e:
        print(f">>> REDACTION ERROR: {e}")
        return img_obj

def save_redacted_image(img_obj, original_filename):
    """Saves the PIL Image object to a secure local 'vault' folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"CLEANSED_{timestamp}_{original_filename.replace('.pdf', '.jpg')}"
    file_path = os.path.join(REDACTED_DIR, safe_name)
    img_obj.save(file_path, format="JPEG")
    print(f">>> STORAGE: Redacted image saved to {file_path}")
    return file_path

def extract_invoice_data(file_bytes):
    print(">>> AZURE: Starting Surgical Extraction...")
    poller = doc_client.begin_analyze_document(model_id="prebuilt-invoice", body=file_bytes)
    result = poller.result()
    
    data = {"vendor": "N/A", "total": "0.00", "tax": "0.00", "date": "N/A", "items": [], "pii_coords": []}
    
    if result.documents:
        doc = result.documents[0]
        fields = doc.fields
        
        # 1. Capture Audit Data (Do NOT redact these)
        data["vendor"] = fields.get("VendorName", {}).get("content", "N/A")
        data["total"] = fields.get("InvoiceTotal", {}).get("content", "0.00")
        data["date"] = fields.get("InvoiceDate", {}).get("content", "N/A")
        tax_f = fields.get("TotalTax") or fields.get("Tax")
        data["tax"] = tax_f.get("content", "0.00") if tax_f else "0.00"

        # 2. SURGICAL REDACTION: Only target Customer PII
        # We target specific fields identified by Azure as "Customer" or "Address"
        sensitive_targets = ["CustomerName", "BillingAddress", "ShippingAddress", "CustomerAddress"]
        
        for target in sensitive_targets:
            field_data = fields.get(target)
            if field_data and field_data.get("boundingRegions"):
                for region in field_data["boundingRegions"]:
                    poly = region.get("polygon")
                    if poly:
                        # Convert to flat list [x,y,x,y...]
                        if not isinstance(poly[0], (int, float)):
                            poly = [val for pt in poly for val in (pt.x, pt.y)]
                        
                        # Normalize to 0-1000 scale
                        a_w = result.pages[region.page_number - 1].width
                        a_h = result.pages[region.page_number - 1].height
                        scaled = []
                        for i in range(0, 8, 2):
                            scaled.append((poly[i] / a_w) * 1000)
                            scaled.append((poly[i+1] / a_h) * 1000)
                        data["pii_coords"].append(scaled)
    
    print(f">>> ENGINE: Captured {len(data['pii_coords'])} surgical redaction zones.")
    return data

def security_audit(file_bytes, extracted_data, is_pdf=False, original_name="invoice.pdf"):
    """PHASE 2: Global Audit + Redaction Execution"""
    try:
        # 1. Convert/Load to PIL Image first
        if is_pdf:
            poppler_bin = os.path.normpath(os.getenv("POPPLER_PATH"))
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1, poppler_path=poppler_bin)
            working_img = images[0]
        else:
            working_img = Image.open(io.BytesIO(file_bytes))

        # 2. Apply Redaction and Save if coordinates exist
        if extracted_data.get("pii_coords"):
            working_img = apply_redaction(working_img, extracted_data["pii_coords"])
            save_redacted_image(working_img, original_name)

        # 3. Prepare for OpenAI (Bytes + Base64)
        img_byte_arr = io.BytesIO()
        working_img.save(img_byte_arr, format='JPEG')
        final_bytes = img_byte_arr.getvalue()
        base64_image = base64.b64encode(final_bytes).decode('utf-8')

        now = datetime.now()
        today_str = now.strftime("%d.%m.%Y")
        current_year = now.year 

        # 4. Perform Audit with your original Persona and Rules
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
        print(f"Audit Error: {e}")
        return f"Audit failed: {e}"