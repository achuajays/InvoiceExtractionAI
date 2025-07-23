import base64
from google import genai
import os
from models import InvoiceData
import logging
from dotenv  import load_dotenv

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
            Extract ONLY the following invoice details from the image. Return the data in JSON format:

{
  "party_name": "",
  "party_name_translated": "",
  "date": "",
  "invoice_number": "",
  "seller_vat_number": "",
  "client_vat_number": "",
  "total_amount": "",
  "vendor_address": "",
  "vendor_address_translated": "",
  "detected_language": "",
  "items": [
    {
      "name": "",
      "name_translated": "",
      "quantity": "",
      "cost": ""
    }
  ]
}

EXTRACTION GUIDELINES:
1. Extract text in both English and Arabic where available
2. For dates, use DD/MM/YYYY format
3. For amounts, include currency and decimal values
4. If a field is not visible, use empty string ""
5. For items array, include all line items from the invoice table
6. Look for VAT numbers in header/footer sections
7. Party name = client/customer name
8. Vendor address = seller/company address
9. Detected language should be "Arabic" or "English" or "Bilingual"
10. Match English and Arabic versions of the same field

IMPORTANT: Only extract the requested fields. Do not add extra information.
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
