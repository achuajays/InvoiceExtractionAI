import base64
import logging
import os

import openai
from dotenv import load_dotenv

from src.models.extraction_models import InvoiceDataExtracted

load_dotenv(dotenv_path=".env")
print("API Key:", os.getenv("OPENAI_API_KEY"))


class InvoiceExtractorOPENAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = (
            "gpt-5-mini-2025-08-07"  # or "gpt-4-vision-preview" if you have access
        )

    def extract(self, image_path: str) -> InvoiceDataExtracted:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
            # Construct the image data for OpenAI API according to requirements
            image_data = {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"},
            }
            prompt = """
You are a specialized, AI-powered data extraction engine. Your mission is to meticulously analyze the provided document image and extract information exclusively about the Biller/Seller. The Biller is the entity that issued the document (e.g., the store, the bank, the utility company).

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
  "detected_language": "",
  "discount": "",
  "currency": ""
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

Field Definitions & Extraction Guidelines
Biller / Seller Information

Focus solely on the company that issued the document. Actively ignore any sections labeled "Customer", "Recipient", "Beneficiary", "Bill To", or "Ship To".

partner: The full legal or trading name of the company/business that issued the document.Must be extract the correct partner name that is visible in the image.Must be extracted from Header section,if not found in header section then extract from footer section.

vat_number: Objective- Accurately extract the 15-digit VAT Registration Number (VAT Number), also known as a Tax Registration Number (TRN), from the provided document or image. VAT Number Definition- The VAT Number is an official, unique 15-digit numeric identifier assigned for tax purposes. Core Instructions & Rules- High-Accuracy OCR- Use an OCR process optimized for numeric fields. Apply advanced validation to correct common character recognition errors (e.g., mistaking 'O' for '0', 'I' or 'l' for '1', 'S' for '5', 'B' for '8'). Whitespace Trimming- You must identify and completely remove any leading or trailing spaces from the extracted number. Strict 15-Digit Format- The final, extracted number must be exactly 15 digits long and contain only numeric characters (0-9). Mandatory Two-Step Verification Process- Step 1- Extraction (First Expert Role)- Scan the entire document to locate the most likely candidate for the VAT Number. Prioritize numbers explicitly labeled "VAT Number", "TRN", "Tax Registration Number", or a similar identifier. Perform the initial extraction, applying the OCR corrections and whitespace removal rules. Step 2- Verification (Second Expert Role)- After the initial extraction, you must rigorously verify its correctness by confirming it against the following checklist- Length Check- Is the number exactly 15 digits long after trimming spaces? Content Check- Does it contain only numbers (0-9)? Context Check- Re-examine the document. Is this number definitively in the VAT Number/TRN field? Are there other plausible 15-digit numbers that might be the correct one? Confidence Check- Re-read the specific digits of your candidate number multiple times to ensure high confidence in each digit. Correction- If your initial extraction fails any verification check, you must repeat the process to find the correct number that satisfies all rules. Output Format- Return only the final, verified 15-digit VAT Number. Do not include any labels, explanations, surrounding text, or apologies. Example- If the document contains 'VAT Number- 123456789012345 ', your entire output must be- 123456789012345.

Crucial Rule: This is the company's permanent tax ID. Do not confuse it with a transactional "VAT Invoice Number". If you find only an invoice-specific VAT number but not the company's registration number, leave this field empty.

cr_number: Objective- Your primary objective is to accurately extract the 10-character Commercial Registration number (CR number) from the provided document or image. CR Number Definition- The Commercial Registration number (CR number) is a unique 10-character identifier for a business entity. Look for labels such as "C.R.", "CRN", or "Commercial Registration". Core Instructions & Rules- High-Accuracy OCR- Use an OCR process optimized for alphanumeric fields. Apply advanced validation to correct common character recognition errors (e.g., mistaking 'O' for '0', 'I' or 'l' for '1', 'S' for '5', 'B' for '8'). Whitespace Trimming- You must identify and completely remove any leading or trailing spaces from the extracted number. Strict 10-Character Format- The final, extracted identifier must be exactly 10 characters long. Mandatory Two-Step Verification Process- Step 1- Extraction (First Expert Role)- Scan the entire document to locate the most likely candidate for the CR number. Prioritize identifiers explicitly labeled "C.R.", "CRN", or "Commercial Registration". Perform the initial extraction, applying the OCR corrections and whitespace removal rules. Step 2- Verification (Second Expert Role)- After the initial extraction, you must rigorously verify its correctness by confirming it against the following checklist- Length Check- Is the identifier exactly 10 characters long after trimming spaces? Content Check- Does it contain the expected alphanumeric characters? Context Check- Re-examine the document. Is this identifier definitively in the Commercial Registration field? Are there other plausible 10-character identifiers that might be the correct one? Confidence Check- Re-read the specific characters of your candidate number multiple times to ensure high confidence in each one. Correction- If your initial extraction fails any verification check, you must repeat the process to find the correct identifier that satisfies all rules. Output Format- Return only the final, verified 10-character CR number. Do not include any labels, explanations, surrounding text, or apologies. Example- If the document contains 'Commercial Registration- 1234567890 ', your entire output must be- 1234567890.

street & street2:

If the address is on a single line: Extract the entire address line into the street field and leave street2 as an empty string "".

If the address is on two distinct lines: Extract the first line into street and the second line into street2.
If the vat_number is not found, leave it as an empty string "None".

city: The city from the biller's address.

country: The country from the biller's address.

email: The contact email address of the biller.

mobile: The primary contact phone number. Look for labels like "Phone", "Tel", "Mobile", "Contact No.". You must remove all non-digit characters (spaces, hyphens, parentheses, '+'). Example: "+966 (11) 123-4567" becomes "966111234567".

Document-Level Details

invoice_type: The main title of the document (e.g., "Tax Invoice", "Receipt"). If no title is present, infer the type from its content (e.g., "Bank Transaction Slip", "Payment Confirmation").

invoice_bill_date: The date the document was issued. You must format this as YYYY-MM-DD. Example: "25 Jan 2024" becomes "2024-01-25".Must extract the correct date when the invoice is issued.

reference: The unique identifier for this document. Look for "Invoice No.", "Reference Number", "Transaction ID".

detected_language: The primary language of the text in the document (e.g., "Arabic", "English", "Mixed").

discount: The total discount amount applied to the invoice. Look for fields like "Discount", "Discount Amount", "Total Discount". Strip all currency symbols and commas. If no discount is mentioned, use "0".

currency: The currency used in the document (e.g., "SAR", "USD", "EUR"). Look for currency symbols or abbreviations throughout the document.Must be 3 characters long.Example: "SAR".Extract correctly after removing any leading or trailing spaces.

Line Item Details (invoice_lines)

Guideline: For bank slips or payment confirmations, invoice_lines should only contain fees or charges levied by the biller (e.g., "Service Fee", "VAT on Fee"). The main transaction amount is not a line item.

For each item in the invoice_lines array:

product: A string describing the product or service charge. take it even if its in arabic.Do not extract or include information related to warranties, return policies, websites, or promotional text. Focus exclusively on the defined data points.


gross_amount: A string representing the total price for the line item before taxes (typically Quantity × Unit Price). Look for column headers like 'Amount', 'Subtotal', or 'Total'. Strip all currency symbols and commas.Only extract the numeric value.Return only the numeric value.

unit_price: A string representing the price per unit. Strip all currency symbols and commas.Only extract the numeric value.Return only the numeric value.Unit price must be extracted after applying discount.

quantity: A string representing the quantity.

taxes: A string representing the tax applied to the line item.

MANDATORY RULES & CONSTRAINTS

JSON ONLY OUTPUT: Your entire response must be a single, raw JSON object. No explanations or code fences.

STRICT SCHEMA ADHERENCE: You must include all keys from the schemas in your response, even if their values are empty.

THE GOLDEN RULE FOR MISSING VALUES:

A) Non-Numeric Fields: For any field that is not a number (e.g., partner, street, email, street2, currency), if the information cannot be found, you MUST use "None" as the value.

B) Numeric Fields: For fields within invoice_lines that represent a monetary value (unit_price, gross_amount) and the discount field, if a value is not present or cannot be read, you MUST use the string "0".

QUANTITY DEFAULT: For the quantity field in invoice_lines, if it is not explicitly stated on the document, you MUST use the string "1".

STRICT TAX FORMATTING: For the taxes field inside each line item, the value MUST be either "0" or "15%". If no tax is mentioned for a line item, use "0". No other tax values are permitted.

DATA EXCLUSION: Do not extract or include information related to warranties, return policies, websites, or promotional text. Focus exclusively on the defined data points.
            """

            messages = [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}, image_data],
                },
            ]

            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )
            import json

            return InvoiceDataExtracted(
                **json.loads(response.choices[0].message.content)
            )
        except Exception as e:
            logging.error(f"Extraction failed: {e}")
            return None
