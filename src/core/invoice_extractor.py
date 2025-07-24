import base64
from google import genai
import os
from models import InvoiceData
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
print("API Key:", os.getenv("GEMINI_API_KEY"))


class InvoiceExtractor:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def extract(self, image_path: str) -> InvoiceData:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = """
            
                # Invoice Data Extraction Prompt

Extract the following information from this invoice/bill image. Focus on the BILLER/SELLER information (not the customer/buyer). Return data in JSON format with these exact keys:

```json
{
  "Partner": "",
  "VAT_NUMBER": "",
  "CR_NUMBER": "",
  "Street": "",
  "Street2": "",
  "Country": "",
  "Email": "",
  "City": "",
  "Mobile": "",
  "INVOICE_TYPE": "",
  "Invoice_Bill_Date": "",
  "Reference": "",
  "Invoice_lines_Product": [],
  "Invoice_lines_Quantity": [],
  "Invoice_lines_Unit_Price": [],
  "Invoice_lines_Taxes": []
}
```

## Extraction Guidelines:

**BILLER/SELLER Information (TOP SECTION):**
- **Partner**: Company/business name issuing the invoice
- **VAT_NUMBER**: VAT registration number of the biller
- **CR_NUMBER**: Commercial registration number of the biller
- **Street**: Primary street address of the biller
- **Street2**: Secondary address line (apartment, suite, etc.)
- **Country**: Country of the biller
- **Email**: Contact email of the biller
- **City**: City of the biller
- **Mobile**: Phone/mobile number of the biller

**Invoice Details:**
- **INVOICE_TYPE**: Type (Invoice, Bill, Credit Note, etc.)
- **Invoice_Bill_Date**: Date when invoice was issued
- **Reference**: Invoice number or reference ID

**Line Items (Arrays - maintain same order):**
- **Invoice_lines_Product**: Product/service descriptions
- **Invoice_lines_Quantity**: Quantities for each item
- **Invoice_lines_Unit_Price**: Unit price for each item
- **Invoice_lines_Taxes**: Tax amount or rate for each item

## Important Rules:
1. If any field is not visible or not present, use "none"
2. For arrays, if no line items exist, use empty arrays []
3. Extract only BILLER information, ignore customer details
4. Look for common variations: VAT No., Tax ID, TRN, etc.
5. Dates should be in original format shown
6. Prices should include currency symbol if visible
7. Return ONLY the JSON object, no additional text

DO NOT OUTPUT ANYTHING OTHER THAN VALID JSON.
            """
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_base64}},
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": InvoiceData,
                },
            )

            return response.parsed
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return None
