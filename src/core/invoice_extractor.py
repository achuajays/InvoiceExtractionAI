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
  "partner": "",
  "vat_number": "",
  "cr_number": "",
  "street": "",
  "street2": "",
  "country": "",
  "email": "",
  "city": "",
  "mobile": "",
  "invoice_type": "",
  "invoice_bill_date": "",
  "reference": "",
  "detected_language": "",
  "invoice_lines": [
    {
      "product": "",
      "quantity": "",
      "unit_price": "",
      "taxes": ""
    }
  ]
}

EXTRACTION GUIDELINES:
1. Partner: Extract the client/customer/partner name
2. VAT Number: Look for VAT registration number (seller or main VAT number)
3. CR Number: Extract Commercial Registration number if available
4. Street: Primary address line/street
5. Street2: Secondary address line if available
6. Country: Country name from address
7. Email: Email address if visible
8. City: City name from address
9. Mobile: Phone/mobile number if available
10. Invoice Type: Type of invoice (e.g., "Invoice", "Tax Invoice", "Bill", etc.)
11. Invoice/Bill Date: Date in DD/MM/YYYY format
12. Reference: Invoice number or reference number
13. Invoice Lines: All line items with product name, quantity, unit price, and tax amount
14. Detected language should be "Arabic", "English", or "Bilingual"
15. If a field is not visible or not applicable, use empty string ""
16. For amounts, include only numeric values without currency symbols
17. Extract all line items from the invoice table/list

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
