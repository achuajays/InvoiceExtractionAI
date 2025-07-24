import base64
from google import genai
import os
from models import InvoiceData
import logging
from dotenv import load_dotenv
from pdf_converter import PDFConverter
from src.core.image_preprocessor import ImagePreprocessor

load_dotenv(dotenv_path=".env")

class CustomInvoiceExtractor:
    def __init__(self, output_folder: str = "temp_images"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.pdf_converter = PDFConverter(output_folder)
        self.preprocessor = ImagePreprocessor()
        
    def extract_custom_fields(self, pdf_path: str, requested_fields: dict, preprocess=True) -> dict:
        """
        Extract custom fields from PDF based on user specifications.
        
        Args:
            pdf_path: Path to the PDF file
            requested_fields: Dictionary of field_name: description
            preprocess: Whether to preprocess images
            
        Returns:
            Dictionary with extracted custom fields
        """
        try:
            # Convert PDF to images
            image_paths = self.pdf_converter.convert(pdf_path)
            
            if not image_paths:
                raise ValueError("Failed to convert PDF to images")
            
            # Process the first image (you can extend this to handle multiple pages)
            image_path = image_paths[0]
            
            if preprocess:
                image_path = self.preprocessor.preprocess(image_path)
            
            # Extract custom fields using AI
            custom_data = self._extract_with_ai(image_path, requested_fields)
            
            return custom_data
            
        except Exception as e:
            logging.error(f"Custom extraction failed: {e}")
            raise ValueError(f"Custom extraction failed: {str(e)}")
    
    def _extract_with_ai(self, image_path: str, requested_fields: dict) -> dict:
        """
        Use AI to extract the requested fields from the image.
        """
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")
            
            # Build dynamic prompt based on requested fields
            fields_prompt = self._build_fields_prompt(requested_fields)
            
            prompt = f"""
            Extract ONLY the following specific fields from the invoice image. Return the data in JSON format:
            
            {fields_prompt}
            
            EXTRACTION GUIDELINES:
            1. Extract text in both English and Arabic where available
            2. For dates, use DD/MM/YYYY format
            3. For amounts, include only numeric values without currency symbols
            4. If a field is not visible or not applicable, use empty string ""
            5. Look for information in headers, footers, and main content areas
            6. Be precise and extract only what is requested
            7. For line items, include all relevant entries from tables
            
            IMPORTANT: Only extract the requested fields. Do not add extra information.
            Return the result as a valid JSON object.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/png", "data": img_base64}},
                ],
                config={
                    "response_mime_type": "application/json",
                },
            )
            
            # Parse the response
            import json
            extracted_data = json.loads(response.text)
            
            return extracted_data
            
        except Exception as e:
            logging.error(f"AI extraction failed: {e}")
            return {field: "" for field in requested_fields.keys()}
    
    def _build_fields_prompt(self, requested_fields: dict) -> str:
        """
        Build a dynamic prompt based on requested fields.
        """
        fields_json = {}
        field_descriptions = []
        
        for field_name, description in requested_fields.items():
            fields_json[field_name] = ""
            field_descriptions.append(f"- {field_name}: {description}")
        
        json_structure = json.dumps(fields_json, indent=2)
        descriptions_text = "\n".join(field_descriptions)
        
        return f"""
JSON Structure to return:
{json_structure}

Field Descriptions:
{descriptions_text}
        """

    def extract_predefined_fields(self, pdf_path: str, field_set: str = "basic") -> dict:
        """
        Extract predefined sets of fields for common use cases.
        
        Args:
            pdf_path: Path to the PDF file
            field_set: Type of field set ("basic", "detailed", "accounting")
            
        Returns:
            Dictionary with extracted fields
        """
        predefined_fields = {
            "basic": {
                "partner": "Company or client name",
                "invoice_bill_date": "Invoice date",
                "reference": "Invoice number or reference",
                "total_amount": "Total invoice amount"
            },
            "detailed": {
                "partner": "Company or client name",
                "vat_number": "VAT registration number",
                "invoice_bill_date": "Invoice date",
                "reference": "Invoice number or reference",
                "street": "Address street",
                "city": "City name",
                "country": "Country name",
                "email": "Email address",
                "mobile": "Phone number"
            },
            "accounting": {
                "partner": "Company or client name",
                "vat_number": "VAT registration number",
                "cr_number": "Commercial registration number",
                "invoice_type": "Type of invoice",
                "invoice_bill_date": "Invoice date",
                "reference": "Invoice number or reference",
                "invoice_lines": "All line items with product, quantity, price, taxes",
                "total_amount": "Total invoice amount",
                "tax_amount": "Total tax amount"
            }
        }
        
        if field_set not in predefined_fields:
            raise ValueError(f"Unknown field set: {field_set}. Available: {list(predefined_fields.keys())}")
        
        return self.extract_custom_fields(pdf_path, predefined_fields[field_set])
