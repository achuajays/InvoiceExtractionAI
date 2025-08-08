import base64
import logging
import os

from dotenv import load_dotenv
from google import genai

from src.models.extraction_models import InvoiceDataExtracted

load_dotenv(dotenv_path=".env")
print("API Key:", os.getenv("GEMINI_API_KEY"))


class InvoiceExtractorGEMINI:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def extract(self, image_path: str) -> InvoiceDataExtracted:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = """You are a specialized invoice data extraction engine. Your mission is to meticulously analyze the provided document image and extract information exclusively about the Biller/Seller. The Biller is the entity that issued the document (e.g., the store, the bank, the utility company).

You must return a single, valid JSON object. Adhere strictly to the schema and rules below. Do not include any introductory text, explanations, or markdown code fences (```json).

Output Schema

The entire output must be a single JSON object using these exact keys:

Generated json
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

Line Item Schema

For the invoice_lines array, each line item must use this exact structure:

Generated json
{
  "product": "Product/service name",
  "quantity": "Quantity or amount",
  "unit_price": "Price per unit",
  "gross_amount": "Total amount before tax",
  "taxes": "Tax amount or percentage"
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END
Field Definitions & Extraction Guidelines
Biller / Seller Information

Focus solely on the company that issued the document. Actively ignore any sections labeled "Customer", "Recipient", "Beneficiary", "Bill To", or "Ship To".

partner: The full legal or trading name of the company/business that issued the document.

vat_number: The company's official VAT Registration Number (e.g., TRN).

Crucial Rule: This is the company's permanent tax ID. Do not confuse it with a transactional "VAT Invoice Number". If you only find an invoice-specific VAT number but not the company's registration number, leave this field as an empty string "".

cr_number: The Commercial Registration number. Look for labels like "C.R.", "CRN", or "Commercial Registration".

street: The primary street name and number from the biller's address.

street2: The secondary address line (e.g., building name, floor). If not present, use "".

city: The city from the biller's address.

country: The country of the biller's address.

email: The contact email address of the biller.

mobile: The primary contact phone or mobile number of the biller. You must remove all spaces, hyphens, and parentheses (e.g., "+966 (11) 123-4567" becomes "966111234567").

Document-Level Details

invoice_type: check if the document is a tax invoice or a receipt. if it is a tax invoice, return True, otherwise return False.

invoice_bill_date: The date the document was issued. You must format this as YYYY-MM-DD. For example, "25 Jan 2024" or "25/01/2024" becomes "2024-01-25".

reference: The unique identifier for this specific document or transaction. Look for "Invoice No.", "Reference Number", "Transaction ID", or a similar unique code.

detected_language: The primary language of the text in the document (e.g., "Arabic", "English", "Mixed").

Line Item Details (invoice_lines)

Guideline for Transaction Slips: For bank slips or payment confirmations, invoice_lines should only contain the fees or charges levied by the biller (the bank). Examples include "SADAD Fee", "Commission", "Service Charge", "VAT on Fee". The main transaction amount being transferred is not a line item.

For each item in the invoice_lines array:

product: A string describing the product or service charge.

quantity: A string representing the quantity. If not explicitly stated, you must use "1".

unit_price: A string representing the price per unit. You must strip all currency symbols and thousand separators. If the price is not present, you must use "0".

gross_amount: A string representing the total price for the line item before taxes are applied (typically Quantity × Unit Price). Strip all currency symbols and thousand separators. If this value is not present or cannot be calculated, you must use "0".

taxes: A string representing the tax applied to the line item.

Mandatory Rules & Constraints

JSON Only Output: Your entire response must be a single, raw JSON object and nothing else.

Schema Adherence: You must include all keys from the schemas in your response.

Handling Missing Data:

If a value for any top-level key cannot be found in the document, you must use an empty string "".

If there are no applicable service fees or charges to list, you must use an empty array [] for the invoice_lines key.

Numeric Value Rule: Within invoice_lines, if a numeric value is not found, you must use the string "0". 

Tax Formatting Rule: For the taxes field inside each line item, the value MUST be either "0" or "15%". If no tax is mentioned for a line item, use "0". No other tax values are permitted.

Data Exclusion: Do not extract or include any information related to product warranties, return policies, website addresses (unless it's an email), or general promotional text. Focus exclusively on the data points defined in the schema.

            """
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_base64}},
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": InvoiceDataExtracted,
                },
            )

            return response.parsed
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return None
