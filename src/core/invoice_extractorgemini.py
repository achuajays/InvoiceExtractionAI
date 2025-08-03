import base64
from google import genai
import os
from models import InvoiceData
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
print("API Key:", os.getenv("GEMINI_API_KEY"))


class InvoiceExtractorGEMINI:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def extract(self, image_path: str) -> InvoiceData:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = """You are an expert data extraction engine. Your task is to analyze the provided document image and extract specific information, focusing exclusively on the Biller/Seller's details. The Biller is the entity that issued the document or is charging for a service (e.g., the bank charging a fee, the utility company). You must return the extracted data in a strict JSON format according to the schema and rules below.

                Input:
                An image of an invoice, bill, receipt, or transaction slip.

                Output Schema:
                You must return ONLY a single, valid JSON object. Do not include any introductory text, explanations, or markdown code fences (like ```json). The JSON object must use these exact keys:
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
                Field Definitions & Extraction Guidelines
                Biller / Seller Information
                This is the company that issued the document. For a bank slip, the Biller is the Bank. For a store receipt, the Biller is the Store. Actively ignore any sections labeled "Customer", "Recipient", "Beneficiary", "Bill To", or "Ship To".

                Partner: The full legal or trading name of the company/business issuing the document (e.g., "Alinma Bank").

                VAT_NUMBER: The company's official VAT Registration Number (TRN).

                Crucial Rule: Do not confuse this with a transactional "VAT Invoice Number". A VAT Registration number is a permanent ID for the company. If you find a "VAT Invoice Number" but no company VAT Reg. No., set this field to "none".

                CR_NUMBER: The Commercial Registration number. Look for "C.R.", "CRN", "Commercial Registration".

                Street: The primary street name and number of the biller's address.

                Street2: Secondary address line (e.g., building, floor). If not present, use "none".

                City: The city from the biller's address.

                Country: The country of the biller.

                Email: The contact email address of the biller.

                Mobile: The contact phone number of the biller. Extract the primary number and remove spaces or special characters (e.g., "800-120-1010" becomes "8001201010").

                Document-Level Details

                INVOICE_TYPE: The main title of the document.

                Examples: "Tax Invoice", "Receipt", "Credit Note". If no title is present, infer from the document's nature, such as "Bank Transaction Slip" or "Payment Confirmation".

                Invoice_Bill_Date: The date the document was issued. You must format this as YYYY-MM-DD. For example, "19/11/2024" becomes "2024-11-19".

                Reference: The unique identifier for the transaction.

                Look for "Invoice No.", "Reference Number", "Transaction ID". On a bank slip, this is the long transaction reference.

                Line Item Details

                Guideline for Transaction Slips: Line items are the specific fees or charges levied by the biller. The main amount being transferred or paid is not a line item. Focus on charges like "Commission", "Service Fee", "VAT Tax", etc.

                Invoice_lines_Product: An array of strings describing each service charge (e.g., ["Commission"]).

                Invoice_lines_Quantity: An array of numbers for the quantity of each service. If not specified, assume 1.

                Invoice_lines_Unit_Price: An array of numbers for the price of each service. Strip all currency symbols and commas.

                Invoice_lines_Taxes: An array of strings or numbers for the tax applied to each line item.The taxes are mostly in percentage.

                Mandatory Rules
                JSON Only: The entire output must be a single, raw JSON object.

                Completeness: You must include all keys from the schema.

                Missing Information: If a value cannot be found, you must use the string "none".

                Empty Line Items: If there are no service fees or charges listed, the four Invoice_lines_ keys must have empty arrays [] as their value.
            """
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
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
