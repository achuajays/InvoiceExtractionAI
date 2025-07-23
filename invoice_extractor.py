import base64
from google import genai
from models import InvoiceData
import logging

class InvoiceExtractor:
    def __init__(self):
        self.client = genai.Client(api_key="")


    def extract(self, image_path: str) -> InvoiceData:
        try:
            with open(image_path, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode("utf-8")

            prompt = """
            
            
            """ # As in your original

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
