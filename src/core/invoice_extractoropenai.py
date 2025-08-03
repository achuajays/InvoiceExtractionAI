import openai
import base64
import os
import logging
from dotenv import load_dotenv
from src.models.extraction_models import InvoiceDataExtracted

load_dotenv(dotenv_path=".env")
print("API Key:", os.getenv("OPENAI_API_KEY"))


class InvoiceExtractorOPENAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4.1-2025-04-14"  # or "gpt-4-vision-preview" if you have access

    def extract(self, image_path: str) -> InvoiceDataExtracted:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
            # Construct the image data for OpenAI API according to requirements
            image_data = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            }
            prompt = """
You are an expert data extraction engine. Your task is to analyze the provided document image and extract specific information, focusing exclusively on the Biller/Seller's details. The Biller is the entity that issued the document or is charging for a service (e.g., the bank charging a fee, the utility company). You must return the extracted data in a strict JSON format according to the schema and rules below.

Input:
An image of an invoice, bill, receipt, or transaction slip.

Output Schema:
You must return ONLY a single, valid JSON object. Do not include any introductory text, explanations, or markdown code fences (like ```
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
"invoice_lines": [],
"detected_language": ""
}

For invoice_lines, use this structure for each line item:
{
  "product": "Product/service name",
  "quantity": "Quantity or amount",
  "unit_price": "Price per unit",
  "taxes": "Tax amount or percentage"
}

Mandatory Rules:
- JSON Only: The entire output must be a single, raw JSON object.
- Completeness: You must include all keys from the schema.
- Missing Information: If a value cannot be found, you must use an empty string "".
- Empty Line Items: If there are no line items, use an empty array [] for invoice_lines.
- Language Detection: Detect the primary language of the document and set detected_language.
            """

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt}, image_data]},
            ]

            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1200,
                temperature=0,
                response_format={"type": "json_object"}
            )
            import json
            return InvoiceDataExtracted(**json.loads(response.choices[0].message.content))
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return None
